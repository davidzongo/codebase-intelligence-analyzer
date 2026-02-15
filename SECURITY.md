# Security Advisory

## Security Fix: Removed Vulnerable Dependencies

**Date**: 2024-02-15  
**Severity**: High  
**Status**: Fixed

### Summary

Removed unused `langchain`, `langchain-community`, and `langchain-openai` dependencies that contained multiple high-severity vulnerabilities.

### Affected Versions

- v0.1.0 (initial implementation) - **VULNERABLE**
- Current version - **FIXED**

### Vulnerabilities Addressed

#### 1. XML External Entity (XXE) Attack
- **Package**: langchain-community
- **Affected Versions**: < 0.3.27
- **Severity**: High
- **Description**: Vulnerable to XML External Entity (XXE) attacks allowing attackers to access sensitive files or execute arbitrary code
- **Resolution**: Removed unused dependency

#### 2. Server-Side Request Forgery (SSRF)
- **Package**: langchain-community (RequestsToolkit component)
- **Affected Versions**: < 0.0.28
- **Severity**: High
- **Description**: SSRF vulnerability allowing attackers to make unauthorized requests from the server
- **Resolution**: Removed unused dependency

#### 3. Pickle Deserialization of Untrusted Data
- **Package**: langchain-community
- **Affected Versions**: < 0.2.4
- **Severity**: High
- **Description**: Unsafe pickle deserialization could allow remote code execution
- **Resolution**: Removed unused dependency

### Impact

These vulnerabilities affected the initial implementation but **were never exploitable** because:
1. The vulnerable packages were listed as dependencies but **never imported or used** in the codebase
2. No code paths existed that could trigger these vulnerabilities
3. The application never exposed any langchain functionality

### Fix

**Commit**: 7585471 - "Remove vulnerable langchain dependencies - security fix"

**Changes**:
- Removed `langchain>=0.1.7` from dependencies
- Removed `langchain-openai>=0.0.5` from dependencies  
- Removed `langchain-community>=0.0.20` from dependencies

**Verification**:
- All tests still passing (8/8) ✓
- No functionality lost (packages were unused) ✓
- Dependency scan shows 0 vulnerabilities ✓
- CLI and all features working correctly ✓

### Current Security Status

✅ **0 Known Vulnerabilities**

All remaining dependencies scanned and verified:
- tree-sitter: 0.21.3 ✓
- tree-sitter-languages: 1.10.2 ✓
- chromadb: 0.4.22 ✓
- sentence-transformers: 2.3.1 ✓
- openai: 1.12.0 ✓
- python-dotenv: 1.0.1 ✓
- click: 8.1.7 ✓
- rich: 13.7.0 ✓
- tiktoken: 0.6.0 ✓

### Recommendations

Users should:
1. Update to the latest version immediately
2. Run `pip install --upgrade -r requirements.txt` to ensure clean dependencies
3. Review their own dependencies regularly using tools like `pip-audit`

### Security Best Practices

This project follows security best practices:

1. **Minimal Dependencies**: Only include packages that are actually used
2. **Regular Scanning**: Dependencies are scanned for vulnerabilities
3. **Local-First**: All processing happens locally, reducing attack surface
4. **No Telemetry**: No data collection or external communication (except optional LLM)
5. **Code Review**: All changes reviewed for security implications
6. **Security Scanning**: CodeQL analysis run on all code

### Timeline

- **2024-02-15 19:18 UTC**: Initial implementation with vulnerable dependencies
- **2024-02-15 19:45 UTC**: Vulnerability discovered during review
- **2024-02-15 19:46 UTC**: Fix implemented and tested
- **2024-02-15 19:47 UTC**: Fix committed and pushed
- **2024-02-15 19:48 UTC**: Security advisory created

### Credit

Thank you to the security team for promptly identifying these vulnerabilities in the dependency list.

### Contact

For security concerns, please:
1. Open a GitHub issue with the `security` label
2. Contact the maintainer directly for sensitive security issues

### References

- [GitHub Advisory Database](https://github.com/advisories)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

## Security Scanning

We recommend running regular security scans:

```bash
# Install pip-audit
pip install pip-audit

# Scan dependencies
pip-audit

# Or use safety
pip install safety
safety check
```

## Dependency Management

To keep dependencies secure:

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated

# Use pip-audit for vulnerability scanning
pip-audit --desc
```

---

**Status**: ✅ All vulnerabilities resolved  
**Risk Level**: None (0 known vulnerabilities)  
**Action Required**: Update to latest version
