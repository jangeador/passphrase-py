#  ***************************************************************************
#  This file is part of Passphrase:
#  A cryptographically secure passphrase and password generator
#  Copyright (C) <2017>  <Ivan Ariel Barrera Oro>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***************************************************************************

"""Generate cryptographically secure passphrases, passwords and more.

Passphrases are generated by picking from a word list using cryptographically
secure random number generator. Passwords are generated from printable
characters.

"""

from typing import Union, List, Tuple
from string import digits, ascii_lowercase, ascii_uppercase, punctuation

from .wordlist import EFF_LONG_WORDLIST, EFF_LONG_WORDLIST_ENTROPY
from .calc import password_length_needed as calc_password_length_needed
from .calc import words_amount_needed as calc_words_amount_needed
from .calc import entropy_bits_nrange as calc_entropy_bits_nrange
from .calc import passphrase_entropy as calc_passphrase_entropy
from .calc import password_entropy as calc_password_entropy
from .calc import entropy_bits as calc_entropy_bits
from .secrets import randchoice, randhex, randbetween
from .settings import MIN_NUM, MAX_NUM
from .aux import Aux


__author__ = 'HacKan'
__license__ = 'GNU GPL 3.0+'
__version__ = '0.6.0'


class Passphrase:
    """Generate cryptographically secure passphrases, passwords and more."""

    @property
    def entropy_bits_req(self) -> float:
        """Entropy bits required (desired) to be used for calculations."""
        return self._entropy_bits_req

    @entropy_bits_req.setter
    def entropy_bits_req(self, entropybits: Union[float, int]) -> None:
        if not isinstance(entropybits, (int, float)):
            raise TypeError('entropy_bits_req can only be int or float')
        if entropybits < 0:
            raise ValueError('entropy_bits_req should be greater than 0')
        self._entropy_bits_req = float(entropybits)

    @property
    def randnum_min(self) -> int:
        """Lower bound for passphrases' random number."""
        return self._randnum_min

    @randnum_min.setter
    def randnum_min(self, randnum: int) -> None:
        if not isinstance(randnum, int):
            raise TypeError('randnum_min can only be int')
        if randnum < 0:
            raise ValueError('randnum_min should be greater than 0')
        self._randnum_min = randnum

    @property
    def randnum_max(self) -> int:
        """Upper bound for passphrases' random number."""
        return self._randnum_max

    @randnum_max.setter
    def randnum_max(self, randnum: int) -> None:
        if not isinstance(randnum, int):
            raise TypeError('randnum_max can only be int')
        if randnum < 0:
            raise ValueError('randnum_max should be greater than 0')
        self._randnum_max = randnum

    @property
    def amount_w(self) -> int:
        """Amount of words for the passphrase."""
        return self._amount_w

    @amount_w.setter
    def amount_w(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError('amount_w can only be int')
        if amount < 0:
            raise ValueError('amount_w should be greater than 0')
        self._amount_w = amount

    @property
    def amount_n(self) -> int:
        """Amount of numbers for the passphrase."""
        return self._amount_n

    @amount_n.setter
    def amount_n(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError('amount_n can only be int')
        if amount < 0:
            raise ValueError('amount_n should be greater than 0')
        self._amount_n = amount

    @property
    def passwordlen(self) -> int:
        """Length of the password to be generated."""
        return self._passwordlen

    @passwordlen.setter
    def passwordlen(self, length: int) -> None:
        if not isinstance(length, int):
            raise TypeError('passwordlen can only be int')
        if length < 0:
            raise ValueError('passwordlen should be greater than 0')
        self._passwordlen = length

    @property
    def separator(self) -> str:
        """Passphrase separator character(s)."""
        return self._separator

    @separator.setter
    def separator(self, sep: str) -> None:
        if not isinstance(sep, str):
            raise TypeError('separator can only be string')
        self._separator = sep

    @property
    def wordlist(self) -> list:
        """Wordlist for passphrase generation."""
        return self._wordlist

    @wordlist.setter
    def wordlist(self, words: Union[list, tuple]) -> None:
        if not isinstance(words, (list, tuple)):
            raise TypeError('wordlist can only be list or tuple')
        self._wordlist = list(words)
        self._wordlist_entropy_bits = None

    @property
    def password_use_lowercase(self) -> bool:
        """Set password usage of lowercase characters."""
        return self._password_use_lowercase

    @password_use_lowercase.setter
    def password_use_lowercase(self, use_lowercase: bool) -> None:
        self._password_use_lowercase = bool(use_lowercase)

    @property
    def password_use_uppercase(self) -> bool:
        """Set password usage of uppercase characters."""
        return self._password_use_uppercase

    @password_use_uppercase.setter
    def password_use_uppercase(self, use_uppercase: bool) -> None:
        self._password_use_uppercase = bool(use_uppercase)

    @property
    def password_use_digits(self) -> bool:
        """Set password usage of numerical digits."""
        return self._password_use_digits

    @password_use_digits.setter
    def password_use_digits(self, use_digits: bool) -> None:
        self._password_use_digits = bool(use_digits)

    @property
    def password_use_punctuation(self) -> bool:
        """Set password usage of punctuation characters."""
        return self._password_use_punctuation

    @password_use_punctuation.setter
    def password_use_punctuation(self, use_punctuation: bool) -> None:
        self._password_use_punctuation = bool(use_punctuation)

    @staticmethod
    def _read_words_from_wordfile(inputfile: str) -> list:
        return [
            word.strip() for word in open(inputfile, mode='rt')
        ]

    @staticmethod
    def _read_words_from_diceware(inputfile: str) -> list:
        return [
            word.split()[1] for word in open(inputfile, mode='rt')
        ]

    def _get_password_characters(self, cathegorized=False) -> str:
        group = []

        if self.password_use_lowercase:
            group.append(ascii_lowercase)
        if self.password_use_uppercase:
            group.append(ascii_uppercase)
        if self.password_use_digits:
            group.append(digits)
        if self.password_use_punctuation:
            group.append(punctuation)

        return group if cathegorized else ''.join(group)

    def __init__(self,
                 inputfile: str = None,
                 is_diceware: bool = False) -> None:
        """Generate cryptographically secure passphrases, passwords and more.

        Passphrases are generated by picking from a word list.
        Passwords are generated by picking from a list of printable characters.
        Additionally, UUIDv4 can be generated. Calculations are based on
        entropy but a fixed amount of words or lengths can be set.
        All operations are done using a cryptographically secure random number
        generator derived directly from /dev/urandom.

        Keyword arguments:
        inputfile -- A string with the path to the wordlist file to load, or
        the value 'internal' to load the internal one.
        is_diceware -- True if the file is diceware-like (not needed for
        internal).

        """
        self._randnum_min = MIN_NUM
        self._randnum_max = MAX_NUM
        self._separator = ' '
        self._password_use_lowercase = True
        self._password_use_uppercase = True
        self._password_use_digits = True
        self._password_use_punctuation = True
        self._passwordlen = None
        self._amount_n = None
        self._amount_w = None
        self._entropy_bits_req = None
        self._wordlist = None
        self._wordlist_entropy_bits = None
        self.last_result = None

        if inputfile == 'internal':
            self.load_internal_wordlist()
        elif inputfile is not None:
            self.import_words_from_file(inputfile, is_diceware)

    def __str__(self) -> str:
        """Return elements from the last result separated by the separator."""
        if not self.last_result:
            return ''

        separator_len = len(self.separator)
        rm_last_separator = -separator_len if separator_len > 0 else None
        return ''.join(
            '{}{}'.format(w, self.separator) for w in map(
                str,
                self.last_result
            )
        )[:rm_last_separator:]

    @staticmethod
    def entropy_bits(
            lst: Union[
                List[Union[int, str, float, complex]],
                Tuple[Union[int, str, float, complex]]
            ]
    ) -> float:
        """Calculate the entropy of a wordlist or a numerical range.

        Keyword arguments:
        lst -- A wordlist as list or tuple, or a numerical range as a list:
        (minimum, maximum)

        """
        if not isinstance(lst, (tuple, list)):
            raise TypeError('lst must be a list or a tuple')

        size = len(lst)
        if (
                size == 2
                and isinstance(lst[0], (int, float))
                and isinstance(lst[1], (int, float))
        ):
            return calc_entropy_bits_nrange(lst[0], lst[1])

        return calc_entropy_bits(lst)

    def load_internal_wordlist(self) -> None:
        """Load internal wordlist."""
        self._wordlist = EFF_LONG_WORDLIST
        self._wordlist_entropy_bits = EFF_LONG_WORDLIST_ENTROPY

    def import_words_from_file(self,
                               inputfile: str,
                               is_diceware: bool) -> None:
        """Import words for the wordlist from a given file.

        The file can have a single column with words or be diceware-like
        (two columns).

        Keyword arguments:
        inputfile -- A string with the path to the wordlist file to load, or
        the value 'internal' to load the internal one.
        is_diceware -- True if the file is diceware-like.

        """
        if not Aux.isfile_notempty(inputfile):
            raise FileNotFoundError('Input file does not exists, is not valid '
                                    'or is empty: {}'.format(inputfile))

        self._wordlist_entropy_bits = None
        if is_diceware:
            self._wordlist = self._read_words_from_diceware(inputfile)
        else:
            self._wordlist = self._read_words_from_wordfile(inputfile)

    def password_length_needed(self) -> int:
        """Calculate the needed password length to satisfy the entropy number.

        This is for the given character set.

        """
        characters = self._get_password_characters()
        if (
                self.entropy_bits_req is None
                or not characters
        ):
            raise ValueError("Can't calculate the password length needed: "
                             "entropy_bits_req isn't set or the character "
                             "set is empty")

        return calc_password_length_needed(
            self.entropy_bits_req,
            characters
        )

    def words_amount_needed(self) -> int:
        """Calculate the needed amount of words to satisfy the entropy number.

        This is for the given wordlist.

        """
        if (
                self.entropy_bits_req is None
                or self.amount_n is None
                or not self.wordlist
        ):
            raise ValueError("Can't calculate the words amount needed: "
                             "wordlist is empty or entropy_bits_req or "
                             "amount_n isn't set")

        # Thanks to @julianor for this tip to calculate default amount of
        # entropy: minbitlen/log2(len(wordlist)).
        # I set the minimum entropy bits and calculate the amount of words
        # needed, cosidering the entropy of the wordlist.
        # Then: entropy_w * amount_w + entropy_n * amount_n >= ENTROPY_BITS_MIN
        entropy_n = self.entropy_bits((self.randnum_min, self.randnum_max))

        # The entropy for EFF Large Wordlist is ~12.9, no need to calculate
        entropy_w = self._wordlist_entropy_bits \
            if self._wordlist_entropy_bits \
            else self.entropy_bits(self.wordlist)

        return calc_words_amount_needed(
            self.entropy_bits_req,
            entropy_w,
            entropy_n,
            self.amount_n
        )

    def generated_password_entropy(self) -> float:
        """Calculate the entropy of a password that would be generated."""
        characters = self._get_password_characters()
        if (
                self.passwordlen is None
                or not characters
        ):
            raise ValueError("Can't calculate the password entropy: character"
                             " set is empty or passwordlen isn't set")

        if self.passwordlen == 0:
            return 0.0

        return calc_password_entropy(self.passwordlen, characters)

    def generated_passphrase_entropy(self) -> float:
        """Calculate the entropy of a passphrase that would be generated."""
        if (
                self.amount_w is None
                or self.amount_n is None
                or not self.wordlist
        ):
            raise ValueError("Can't calculate the passphrase entropy: "
                             "wordlist is empty or amount_n or "
                             "amount_w isn't set")

        if self.amount_n == 0 and self.amount_w == 0:
            return 0.0

        entropy_n = self.entropy_bits((self.randnum_min, self.randnum_max))

        # The entropy for EFF Large Wordlist is ~12.9, no need to calculate
        entropy_w = self._wordlist_entropy_bits \
            if self._wordlist_entropy_bits \
            else self.entropy_bits(self.wordlist)

        return calc_passphrase_entropy(
            self.amount_w,
            entropy_w,
            entropy_n,
            self.amount_n
        )

    def generate(self, uppercase: int = None) -> list:
        """Generate a list of words randomly chosen from a wordlist.

        Keyword arguments:
        uppercase -- An integer number indicating how many uppercase
        characters are wanted: bigger than zero means that many characters and
        lower than zero means all uppercase except that many. Use 0 to make
        them all uppercase, and None for no one.

        """
        if (
                self.amount_n is None
                or self.amount_w is None
                or not self.wordlist
        ):
            raise ValueError("Can't generate passphrase: "
                             "wordlist is empty or amount_n or "
                             "amount_w isn't set")

        if uppercase is not None and not isinstance(uppercase, int):
            raise TypeError('uppercase must be an integer number')

        passphrase = []
        for _ in range(0, self.amount_w):
            passphrase.append(randchoice(self.wordlist).lower())

        # Handle uppercase
        lowercase = Aux.lowercase_count(passphrase)
        if passphrase and uppercase is not None:
            if (
                    uppercase < 0
                    and lowercase > (uppercase * -1)
            ):
                uppercase = lowercase + uppercase

            # If it's still negative, then means no uppercase
            if uppercase == 0 or uppercase > lowercase:
                # Make it all uppercase
                passphrase = Aux.make_all_uppercase(passphrase)
            elif uppercase > 0:
                passphrase = Aux.make_chars_uppercase(
                    passphrase,
                    uppercase
                )

        # Handle numbers
        for _ in range(0, self.amount_n):
            passphrase.append(randbetween(self.randnum_min, self.randnum_max))

        self.last_result = passphrase
        return passphrase

    def generate_password(self) -> list:
        """Generate a list of random characters."""
        characterset = self._get_password_characters()
        if (
                self.passwordlen is None
                or not characterset
        ):
            raise ValueError("Can't generate password: character set is "
                             "empty or passwordlen isn't set")

        password = []
        for _ in range(0, self.passwordlen):
            password.append(randchoice(characterset))

        self.last_result = password
        return password

    def generate_uuid4(self) -> list:
        """Generate a list of parts of a UUID version 4 string.

        Usually, these parts are concatenated together using dashes.

        """
        # uuid4: 8-4-4-4-12: xxxxxxxx-xxxx-4xxx-{8,9,a,b}xxx-xxxxxxxxxxxx
        # instead of requesting small amounts of bytes, it's better to do it
        # for the full amount of them.
        hexstr = randhex(30)

        uuid4 = [
            hexstr[:8],
            hexstr[8:12],
            '4' + hexstr[12:15],
            '{:x}{}'.format(randbetween(8, 11), hexstr[15:18]),
            hexstr[18:]
        ]
        self.last_result = uuid4
        return uuid4
