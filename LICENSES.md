# License Information for Included Software

This document provides licensing details for the open-source software samples used in this project. Each entry includes:
- The **name of the software** or dataset.
- The **source repository** where the code was obtained.
- The **license type** under which it is distributed.
- A link to the original license file (if applicable).
- Notes about the portion of the code being used.

---

## **1. Bisect Right (Python Standard Library)**
- **Source:** [Python/cpython](https://github.com/python/cpython)
- **License:** [Python Software Foundation License (PSF)](https://github.com/python/cpython/blob/main/LICENSE)
- **Notes:** The bisect module is part of the Python standard library and follows the PSF license. It provides support for maintaining lists in sorted order without needing to explicitly sort them after insertion.

---

## **2. Egyptian Fraction (SymPy)**
- **Source:** [SymPy/sympy](https://github.com/sympy/sympy/)
- **License:** [BSD License](https://github.com/sympy/sympy/blob/master/LICENSE)
- **Notes:** This function is part of the SymPy symbolic mathematics library. It computes Egyptian fraction representations of rational numbers, expressing fractions as sums of distinct unit fractions.

---

## **3. Encoder (GPT-2)**
- **Source:** [OpenAI/gpt-2](https://github.com/encode/django-rest-framework)
- **License:** [MIT License](https://github.com/openai/gpt-2/blob/master/LICENSE)
- **Notes:** This class is part of OpenAI’s GPT-2 repository. It implements byte-pair encoding (BPE), which encodes text into tokenised subwords for use in transformer-based language models.

---

## **4. HTTP Request (Django REST Framework)**
- **Source:** [encode/Django REST Framework](https://github.com/openai/gpt-2)
- **License:** [License](https://github.com/encode/django-rest-framework/blob/master/LICENSE.md)
- **Notes:** The `Request` class wraps Django’s `HttpRequest`, adding content parsing, method overriding, and authentication support for web APIs. It is central to the request/response cycle in Django REST Framework. Additionally, the `exceptions.py` and `settings.py` script files were copied over, as they are required by `request.py`.

---

## **General Notice**
This project does not modify or redistribute the original software beyond what is permitted under their respective licenses. All credit for the original implementations belongs to the respective authors and maintainers.

For additional information on each license, please refer to the links provided above.