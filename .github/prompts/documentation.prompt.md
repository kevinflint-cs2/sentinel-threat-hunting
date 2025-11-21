---
description: 'Generate comprehensive documentation for modules, examples, and README updates'
agent: 'agent'
---

---
description: 'Generate comprehensive documentation for examples and README updates'
agent: 'agent'
---

# Documentation — Example and README Generation

Create clear, concise, GitHub Flavored Markdown documentation for implemented features including practical examples and README updates.

## Mission

Produce professional, task-focused documentation that enables users to understand, configure, and use new endpoints effectively. Follow GitHub documentation standards with minimal decoration and maximum utility.

## Scope & Preconditions

 - **Documentation Areas:**
    - Root README updates (`./README.md`)
- **Format:** GitHub Flavored Markdown (GFM) exclusively
- **Style:** Clear, direct, professional (Microsoft/Azure documentation tone)
- **Authority:** May create/update documentation files after approval
- **Prerequisites:** Testing and linting phases complete

## Inputs

- **Example Name:** Identifier for the implemented feature or use case
- **Configuration:** Required environment variables and setup
- **Examples:** Sample requests and responses
- **Integration Notes:** How feature fits into existing system

## Documentation Structure

### A) Module Documentation

**File:** `./docs/modules/[MODULENAME].md`

**Purpose:** Explain what the module does, how it integrates, and how to configure it.

**Required Sections:**

1. **Title and Purpose**
   - Module name (H1)
   - Single-sentence purpose statement
   - Brief description (2-3 sentences)

2. **Overview**
   - Capabilities provided
   - External service integration details
   - Key features

3. **Configuration**
   - Required environment variables
   - Setup instructions
   - Authentication details

4. **Usage**
   - Function signatures (if library usage)
   - Integration points
   - Expected inputs/outputs

5. **Architecture Notes** (optional)
   - Design decisions
   - Dependencies
   - Performance considerations

6. **Troubleshooting** (optional)
   - Common issues
   - Error messages and resolutions
   - Known limitations

**Template:**




- [ ] Examples are copy-paste ready and tested
- [ ] README updated with endpoint information
- [ ] All code blocks specify language
- [ ] Tables properly formatted
- [ ] Internal links use relative paths
- [ ] No excessive emojis (max 1 in README header)
- [ ] Tone is direct and professional
- [ ] No grammatical errors or typos
- [ ] Configuration clearly documented
- [ ] Error scenarios covered

## Common Patterns


  "status": "error",

  "error": {

    "msg": "missing 'value' parameter"

  }
}
```
```



## Validation Steps


After generating documentation:

1. **Verify files created:**
   ```bash
   ls -l docs/modules/[module].md

   ls -l docs/examples/[module]-curl.md

   git diff README.md
   ```



2. **Check formatting:**
   - Markdown renders correctly in GitHub preview
   - Code blocks have language specified

   - Tables align properly

   - Links resolve correctly

3. **Test examples:**

   - Copy curl commands and verify they work
   - Check response formats match actual API
   - Ensure error examples are accurate

4. **Review content:**
   - No spelling errors
   - Clear and concise language
   - Professional tone throughout
   - All required sections present

## Related Resources

- [Development Process](./development-process.prompt.md) — Seven-phase workflow
- [Implementation Pattern](./implementation-pattern.prompt.md) — Module structure
- [GitHub Flavored Markdown](https://github.github.com/gfm/) — Official GFM spec
- [GitHub Admonitions](https://github.com/orgs/community/discussions/16925) — Alert syntax
