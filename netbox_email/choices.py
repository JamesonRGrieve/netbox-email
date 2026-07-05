# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the email-infrastructure models. Values match the on-server tokens verbatim
(domain authority mode, mailbox kind, SMTP relay auth mechanism)."""
from utilities.choices import ChoiceSet


class MailDomainTypeChoices(ChoiceSet):
    """How the server treats a domain. ``local`` = it hosts mailboxes for the domain; ``relay`` =
    it accepts and forwards mail for the domain to another server; ``alias`` = the whole domain is
    an alias of another (every address rewrites to the target domain)."""
    LOCAL = "local"
    RELAY = "relay"
    ALIAS = "alias"
    CHOICES = [
        (LOCAL, "Local", "green"),
        (RELAY, "Relay", "blue"),
        (ALIAS, "Alias", "orange"),
    ]


class MailboxTypeChoices(ChoiceSet):
    """Kind of mailbox. ``individual`` = a single person; ``group`` = a distribution list expanding
    to members; ``shared`` = a shared mailbox multiple users access."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    SHARED = "shared"
    CHOICES = [
        (INDIVIDUAL, "Individual", "green"),
        (GROUP, "Group", "purple"),
        (SHARED, "Shared", "blue"),
    ]


class RelayAuthChoices(ChoiceSet):
    """SMTP AUTH mechanism a :class:`MailRelay` uses against its upstream smarthost."""
    NONE = "none"
    PLAIN = "plain"
    LOGIN = "login"
    CRAM_MD5 = "cram_md5"
    CHOICES = [
        (NONE, "None", "gray"),
        (PLAIN, "PLAIN", "blue"),
        (LOGIN, "LOGIN", "cyan"),
        (CRAM_MD5, "CRAM-MD5", "green"),
    ]
