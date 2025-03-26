# Adapted from the GPT-2 repository (https://github.com/openai/gpt-2)

import icontract
import regex as re
from functools import lru_cache

@lru_cache()
def bytes_to_unicode():
    """
    Returns list of utf-8 byte and a corresponding list of unicode strings.
    The reversible bpe codes work on unicode strings.
    This means you need a large # of unicode characters in your vocab if you want to avoid UNKs.
    When you're at something like a 10B token dataset you end up needing around 5K for decent coverage.
    This is a signficant percentage of your normal, say, 32K bpe vocab.
    To avoid that, we want lookup tables between utf-8 bytes and unicode strings.
    And avoids mapping to whitespace/control characters the bpe code barfs on.
    """
    bs = list(range(ord("!"), ord("~")+1))+list(range(ord("¡"), ord("¬")+1))+list(range(ord("®"), ord("ÿ")+1))
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8+n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))

def get_pairs(word):
    """Return set of symbol pairs in a word.

    Word is represented as tuple of symbols (symbols being variable-length strings).
    """
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs


@icontract.invariant(
    lambda self: all(isinstance(k, str) and isinstance(v, int) for k, v in self.encoder.items()),
    "Encoder dictionary must map strings to integers."
)
@icontract.invariant(
    lambda self: all(isinstance(k, int) and isinstance(v, str) for k, v in self.decoder.items()),
    "Decoder dictionary must map integers back to strings."
)
class Encoder:
    """
    An Encoder class implementing Byte-Pair Encoding (BPE) as used in GPT-2.

    This class converts text to tokenised integer representations and vice versa
    using a predefined vocabulary and a set of BPE merge rules. A caching mechanism is
    employed to improve efficiency.
    """

    @icontract.require(
        lambda encoder: encoder and all(isinstance(k, str) and isinstance(v, int) for k, v in encoder.items()),
        "Encoder must be a non-empty dictionary mapping strings to integers."
    )
    @icontract.require(
        lambda bpe_merges: all(isinstance(pair, tuple) and len(pair) == 2 and all(isinstance(p, str) for p in pair)
                                for pair in bpe_merges),
        "bpe_merges must be a list of string pairs."
    )
    def __init__(self, encoder: dict[str, int], bpe_merges: list[tuple[str, str]], errors: str = 'replace') -> None:
        """
        Initialise the Encoder instance.

        Parameters:
        - encoder (dict[str, int]): A dictionary mapping string tokens to unique integer IDs.
        - bpe_merges (list[tuple[str, str]]): A list of merge operations (each a tuple of two strings) defining the BPE merge rules.
        - errors (str): The error handling scheme for decoding (default is 'replace').

        Preconditions:
        - encoder must be non-empty and map strings to integers.
        - bpe_merges must be a list of 2-tuples of strings.

        Postconditions:
        - self.encoder is set as provided.
        - self.decoder is the inverse mapping of encoder.
        - self.byte_encoder and self.byte_decoder are set using bytes_to_unicode().
        - self.bpe_ranks is a dictionary mapping each BPE merge to its rank.
        - self.cache is initialised as an empty dictionary.
        """
        self.encoder = encoder
        self.decoder = {v: k for k, v in encoder.items()}
        self.errors = errors
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        self.cache = {}

        self.pat = re.compile(
            r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
        )

    @icontract.require(lambda token: isinstance(token, str) and token, 
                       "Token must be a non-empty string.")
    @icontract.ensure(lambda result: isinstance(result, str) and result, 
                      "Result must be a non-empty string.")
    def bpe(self, token: str) -> str:
        """
        Perform Byte-Pair Encoding on a token.

        This method applies the BPE algorithm to merge symbols based on learned merge rules until
        only one symbol remains. The final result is a string with merged symbols separated by spaces.

        Parameters:
        - token (str): A non-empty string representing the token to encode.

        Returns:
        - str: A string with BPE merges applied.

        Preconditions:
        - token must be a non-empty string.

        Postconditions:
        - The result is a non-empty string.
        """
        if token in self.cache:
            return self.cache[token]

        word = tuple(token)
        assert all(isinstance(ch, str) and ch for ch in word),      "Loop invariant: Each character in word must be a non-empty string."

        pairs = get_pairs(word)

        while True:
            assert all(isinstance(ch, str) and ch for ch in word),  "Loop invariant: Each character in word must be a non-empty string."
            assert all(isinstance(pair, tuple) and len(pair) == 2 and all(isinstance(x, str) and x for x in pair)
                       for pair in pairs),                          "Loop invariant: Pairs must be valid 2-tuples of non-empty strings."

            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float('inf')))
            if bigram not in self.bpe_ranks:
                break
            first, second = bigram
            new_word: list[str] = []
            i = 0
            while i < len(word):
                assert 0 <= i <= len(word), "Loop invariant: index i must be within the word's bounds [0, len(word)]."
                try:
                    j = word.index(first, i)
                    new_word.extend(word[i:j])
                    i = j
                except ValueError:
                    new_word.extend(word[i:])
                    break

                if word[i:i+2] == (first, second):
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1

                assert all(isinstance(item, str) for item in new_word), "Loop invariant: new_word must contain only strings."

            word = tuple(new_word)
            if len(word) == 1:
                break
            pairs = get_pairs(word)

        result = ' '.join(word)
        self.cache[token] = result
        return result

    @icontract.require(lambda text: isinstance(text, str), 
                        "Input text must be a string.")
    @icontract.ensure(lambda result: all(isinstance(tok, int) for tok in result), 
                        "Output must be a list of integer tokens.")
    def encode(self, text: str) -> list[int]:
        """
        Encode input text into a list of integer tokens using BPE.

        The method tokenises the input text using a regular expression pattern, converts each token
        into its corresponding byte representation, applies BPE, and then maps the resulting tokens to integers.

        Parameters:
        - text (str): A string of text to encode.

        Returns:
        - list[int]: A list of integers representing the encoded tokens.

        Preconditions:
        - text must be a string.

        Postconditions:
        - The returned list contains only integers.
        """
        bpe_tokens: list[int] = []
        for token in re.findall(self.pat, text):
            assert isinstance(token, str), "Loop invariant: token must be a string."

            token_bytes = token.encode('utf-8')
            token_translated = ''.join(self.byte_encoder[b] for b in token_bytes)
            assert isinstance(token_translated, str) and token_translated, "Loop invariant: token_translated must be a non-empty string."

            bpe_result = self.bpe(token_translated)
            assert isinstance(bpe_result, str) and bpe_result, "Loop invariant: bpe_result must be a non-empty string."

            for bpe_token in bpe_result.split(' '):
                assert isinstance(bpe_token, str) and bpe_token, "Loop invariant: Each bpe_token must be a non-empty string."

                token_int = self.encoder[bpe_token]
                assert isinstance(token_int, int), "Loop invariant: Token mapping must be an integer."

                bpe_tokens.append(token_int)
        return bpe_tokens

    @icontract.require(lambda tokens: all(isinstance(tok, int) for tok in tokens), 
                       "Tokens must be integers.")
    @icontract.ensure(lambda result: isinstance(result, str), 
                      "Decoded result must be a string.")
    def decode(self, tokens: list[int]) -> str:
        """
        Decode a list of integer tokens back into a string.

        Each integer token is mapped to its corresponding string via the decoder dictionary.
        The resulting string is then converted back to bytes and decoded using the specified error handling.

        Parameters:
        - tokens (list[int]): A list of integers representing the encoded tokens.

        Returns:
        - str: A decoded string.

        Preconditions:
        - tokens must be a list of integers.

        Postconditions:
        - The result is a string.
        """
        text = ""
        for token in tokens:
            assert isinstance(token, int), "Loop invariant: Each token must be an integer."
            assert token in self.decoder, "Loop invariant: token not found in decoder mapping."
            text += self.decoder[token]
        decoded_bytes = bytearray()
        for c in text:
            assert isinstance(c, str) and len(c) == 1, "Loop invariant: Each element in text must be a single character."
            decoded_bytes.append(self.byte_decoder[c])
        return decoded_bytes.decode('utf-8', errors=self.errors)