# Password Security - Enhanced Validation

## Overview

The Home Management Platform uses **enhanced password validation** adapted from the battle-tested DockerMate project. This provides robust security for an internet-facing platform.

## Requirements

All passwords must meet these requirements:

1. **Length**: 12-128 characters
2. **Uppercase**: At least one uppercase letter (A-Z)
3. **Lowercase**: At least one lowercase letter (a-z)
4. **Digit**: At least one digit (0-9)
5. **No Weak Patterns**: Must not match common weak patterns

## Pattern Detection

The system detects and rejects three types of weak patterns discovered through extensive testing on the DockerMate project:

### 1. Weak Base Words with Padding

**Most Important Check**: Users often take weak words and add numbers/symbols to meet requirements.

**Rejected Examples**:
- `Password123456` - weak word with numbers
- `123Admin9876` - weak word with numbers on both sides
- `!!!Welcome123` - weak word with symbols and numbers
- `Qwerty123456` - keyboard pattern word with numbers

**Weak Words List**:
- password, admin, welcome, letmein, qwerty
- monkey, dragon, master, login, user
- homelab, docker, home

**Why**: These passwords appear strong but are trivial to guess once you know the pattern.

### 2. Sequential Patterns

**Rejected Examples**:
- Passwords containing: `12345`, `23456`, `34567`, `45678`, `56789`
- Passwords containing: `abcde`, `bcdef`, `qwerty`, `asdfg`, `zxcvb`

**Why**: Sequential patterns are commonly used and easy to guess.

### 3. Repeated Characters

**Rejected Examples**:
- `MyPassword1111` - four repeated digits
- `SecurePass2aaaa` - four repeated letters
- `TestPassword!!!!` - four repeated symbols

**Why**: Repeating the same character 4+ times suggests a lazy password.

## Strong Password Examples

✅ **Accepted Passwords**:
- `CorrectHorseBattery42` - Passphrase style
- `MyDockerHome2026` - Mixed words with year
- `S3cur3Hom3Manag3r` - Leetspeak variation
- `HomeManager!Platform9` - Multiple words with symbol

❌ **Rejected Passwords**:
- `Password123456` - Weak base word
- `Admin2024!!!` - Weak base word with symbols
- `MyPassword12345` - Sequential numbers
- `SecurePass1111` - Repeated digits

## Implementation Details

### Code Location
- **Validation Function**: `backend/app/core/security.py::validate_password_policy()`
- **Schema Validation**: `backend/app/schemas/auth.py`
- **Tests**: `backend/tests/test_password_validation.py`

### Pattern Detection Regex

```python
# Weak base word pattern (case-insensitive)
weak_pattern = r'^[\d!@#$%^&*()_+=\-\[\]{};:,.<>?/\\|~`]*(password|admin|welcome|...)[\d!@#$%^&*()_+=\-\[\]{};:,.<>?/\\|~`]*$'

# Sequential patterns
sequential = r'(12345|23456|34567|...|abcde|qwerty|asdfg|zxcvb)'

# Repeated characters (4+ in a row)
repeated = r'(.)\1{3,}'
```

## Comparison: DockerMate vs Home Management Platform

| Feature | DockerMate | Home Management Platform |
|---------|------------|--------------------------|
| Hash Algorithm | Bcrypt (work factor 12) | Argon2 (modern, OWASP recommended) |
| Min Length | 12 characters | 12 characters |
| Max Length | Not specified | 128 characters |
| Composition | Uppercase, lowercase, digit | Uppercase, lowercase, digit |
| Pattern Detection | Weak words, sequential, repeated | **Same** (adapted directly) |
| Weak Words | 10 common words | 13 words (added homelab, docker, home) |

## Why This Approach?

### Benefits Over NIST Minimum (8 chars, no composition)

1. **Internet-Facing Platform**: Higher security requirements than internal systems
2. **Pattern Detection**: Catches real-world bypass attempts
3. **Battle-Tested**: Validated through DockerMate production use
4. **User-Friendly**: Clear error messages explain requirements

### Edge Cases Handled

DockerMate testing discovered these edge cases:

1. **Unicode Support**: Passwords with emoji work correctly
2. **Whitespace**: Spaces allowed (useful for passphrases)
3. **Case-Insensitive Detection**: "PASSWORD123" caught same as "password123"
4. **Symbol Padding**: "!!!admin!!!" correctly rejected
5. **Number Padding Both Sides**: "123password456" correctly rejected

## Security Recommendations

### For Users

1. **Use Passphrases**: `CorrectHorseBattery42` is stronger and easier to remember than `P@ssw0rd!`
2. **Use Password Managers**: Generate and store unique passwords
3. **Avoid Personal Info**: Don't use names, birthdays, addresses
4. **Change Default Passwords**: Immediately change the default admin password

### For Administrators

1. **Initial Admin Password**: `AdminHomeManager2026` (change immediately)
2. **Force Password Changes**: New users should change temporary passwords
3. **Monitor Failed Logins**: Watch for brute force attempts
4. **Enable MFA**: Multi-factor authentication adds critical second layer

## Testing

All password validation is comprehensively tested:

```bash
# Run password validation tests
docker compose exec app pytest tests/test_password_validation.py -v

# 27 tests covering:
# - Length validation
# - Composition requirements
# - Weak pattern detection
# - Sequential pattern detection
# - Repeated character detection
# - Strong password acceptance
# - Edge cases
```

## Future Enhancements

1. **Breach Detection**: Check passwords against haveibeenpwned.com API
2. **Custom Weak Words**: Allow admins to add organization-specific weak words
3. **Password Strength Meter**: Real-time feedback during password entry
4. **Password History**: Prevent reuse of recent passwords

## References

- **NIST SP 800-63B**: Digital Identity Guidelines
- **DockerMate Project**: https://github.com/BBultitude/DockerMate
- **OWASP Password Storage Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

**Last Updated**: 2026-02-12
**Author**: Claude (adapted from DockerMate)
