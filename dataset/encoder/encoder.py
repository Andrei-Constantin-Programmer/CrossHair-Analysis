# Adapted from the GPT-2 repository (https://github.com/openai/gpt-2)

import icontract
import regex
from functools import lru_cache

@icontract.ensure(
    lambda result: len(result) == 256,
    "The returned dictionary must map exactly 256 keys (0..255)."
)
@lru_cache()
def bytes_to_unicode() -> dict[int, str]:
    """
    Create a reversible mapping between UTF-8 bytes and Unicode strings.

    Returns:
    - dict[int, int] - A dictionary of length 256 mapping each byte 0..255 to a distinct Unicode string.

    Postconditions:
    - The resulting dictionary must map exactly 256 keys.
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

@icontract.require(
    lambda word: len(word) > 0,
    "The 'word' tuple must be non-empty."
)
@icontract.ensure(
    lambda word, result: len(result) <= max(0, len(word) - 1),
    "The number of adjacent pairs cannot exceed len(word) - 1."
)
@icontract.ensure(
    lambda word, result: all((word[i], word[i+1]) in result for i in range(len(word) - 1)),
    "All adjacent pairs in 'word' must appear in the result."
)
def get_pairs(word: tuple[str, ...]) -> set[tuple[str, str]]:
    """
    Return the set of adjacent symbol pairs in 'word'.

    Parameters:
    - word (tuple[str, ...]): A non-empty tuple of strings (symbols).

    Returns:
    - set[tuple[str, str]]: A set of adjacent (prev_char, char) pairs.

    Preconditions: 
    - 'word' must be non-empty.

    Postconditions:
    - The number of adjacent pairs cannot exceed len(word) - 1
    - All adjacent pairs in 'word' must appear in the result.
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
@icontract.invariant(
    lambda self: self.errors in {"strict", "replace", "ignore", "backslashreplace", "xmlcharrefreplace"},
    "errors must be one of the known Python error-handling modes."
)
class Encoder:
    """
    An Encoder class implementing Byte-Pair Encoding (BPE) as used in GPT-2.

    This class converts text to tokenised integer representations and vice versa
    using a predefined vocabulary and a set of BPE merge rules. A caching mechanism is
    employed to improve efficiency.

    inv: all(isinstance(k, str) and isinstance(v, int) for k, v in self.encoder.items())
    inv: all(isinstance(k, int) and isinstance(v, str) for k, v in self.decoder.items())
    inv: self.errors in {"strict", "replace", "ignore", "backslashreplace", "xmlcharrefreplace"}
    """

    @icontract.require(
        lambda encoder: len(encoder) > 0,
        "Encoder must be a non-empty dictionary."
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

        # Should haved added re.IGNORECASE so BPE merges can happen for capitalized versions of contractions - ORIGINAL COMMENT
        self.pat = regex.compile(
            r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""", regex.IGNORECASE # Added fix recommended by the program authors.
        )

    @icontract.require(
        lambda token: len(token) >= 1,
        "Token must be a non-empty string."
    )
    @icontract.ensure(
        lambda token, result: len(token) >= 2 or (len(token) == 1 and (result == token)),
        "If token has exactly 1 character, BPE returns it unchanged."
    )
    @icontract.ensure(
        lambda result: result, 
        "Result must be a non-empty string."
    )
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
        - If the token is one character long, it should be returned unchanged.
        - The result is a non-empty string.
        """
        if token in self.cache:
            return self.cache[token]

        word = tuple(token)
        assert all(isinstance(ch, str) and ch for ch in word),      "Loop invariant: Each character in word must be a non-empty string."

        pairs = get_pairs(word)

        if not pairs:
            self.cache[token] = token
            return token

        while True:
            assert all(isinstance(ch, str) and ch for ch in word),                                          "Loop invariant: Each character in word must be a non-empty string."
            assert all(len(pair) == 2 and all(isinstance(x, str) and x for x in pair) for pair in pairs),   "Loop invariant: Pairs must be valid 2-tuples of non-empty strings."

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
            if not pairs:
                break
            
        result = ' '.join(word)
        self.cache[token] = result
        return result

    @icontract.require(
        lambda text: text.isascii() and text.isalnum(),
        "The text must be alphanumeric."
    )
    @icontract.ensure(
        lambda result: len(result) >= 1,
        "At least one token must be produced for non-empty input."
    )
    @icontract.ensure(
        lambda self, result:
            all(tok in self.decoder for tok in result),
        "All produced tokens must be valid encoder vocabulary entries."
    )
    @icontract.ensure(
        lambda self, result:
            isinstance(self.decode(result), str) and len(self.decode(result)) >= 0,
        "Decoding the result should yield a string (possibly lossy)."
    )
    @icontract.ensure(
        lambda text, result:
            len(result) <= len(text) * 4,
        "The number of tokens should be at most 4x the number of input characters (upper bound)."
    )
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
        for token in self.pat.findall(text):
            token_bytes = token.encode('utf-8')
            token_translated = ''.join(self.byte_encoder[b] for b in token_bytes)
            bpe_result = self.bpe(token_translated)
            for bpe_token in bpe_result.split(' '):
                token_int = self.encoder[bpe_token]
                bpe_tokens.append(token_int)
        return bpe_tokens

    @icontract.require(
        lambda tokens: len(tokens) > 0,
        "The list of tokens must be non-empty."
    )
    @icontract.require(
        lambda self, tokens: all(tok in self.decoder for tok in tokens),
        "All tokens must exist in the decoder vocabulary."
    )
    @icontract.require(
        lambda self, tokens: all(
            all(c in self.byte_decoder for c in self.decoder[tok])
            for tok in tokens
        ),
        "All decoded characters must be mappable via byte_decoder."
    )
    @icontract.ensure(
        lambda result: isinstance(result, str),
        "Decoded result must be a string."
    )
    @icontract.ensure(
        lambda result: len(result) > 0,
        "Decoded result must be non-empty."
    )
    @icontract.ensure(
        lambda result: all(isinstance(c, str) and len(c) == 1 for c in result),
        "Each character in the result must be a single-character string."
    )
    @icontract.ensure(
        lambda self, result:
            isinstance(result.encode('utf-8', errors=self.errors), bytes),
        "Result must be UTF-8 encodable with the specified error handling."
    )
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
            assert token in self.decoder, "Loop invariant: token must be part of the decoder mapping."
            text += self.decoder[token]
        decoded_bytes = bytearray()
        for c in text:
            assert isinstance(c, str) and len(c) == 1, "Loop invariant: Each element in text must be a single character."
            decoded_bytes.append(self.byte_decoder[c])
        return decoded_bytes.decode('utf-8', errors=self.errors)