# Security

Two kinds of report are welcome.

1. **An exploit of the L6 grader.** Submit it as a normal pull request (see the README). CI verifies it and assigns
   an SGX ID. A public PR is fine: the graded answer is data, not code, and the private key is not revealed by it.
2. **A hole in the wargame's own CI** (for example a way to make `record.yml` run code from a pull request, to read
   the L6 key, or to write a scoreboard row without a verified verdict). Please report these privately:
   **Security tab, "Report a vulnerability"** (private vulnerability reporting is enabled on this repository).

There is no bug bounty and no payment. Confirmed reports are credited by handle in HALL_OF_FAME.md if you want.
