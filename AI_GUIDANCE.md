# AI Guidance

ALWAYS adhere to the following points as you are working on this code base:

1. Use `uv` to create our Python virtual env, manage package dependencies, and run scripts.

2. NEVER mask issues by using fallbacks that hide errors. Prefer explicit errors over fallbacks. Fixing issues is the only way to ensure a stable system.

3. Follow good software development practices (like SOLID).

4. Simpler is better.

5. Remember the purpose of this package is to provide its functionality in a clear and maintainable manner. Avoid adding special-cases or hack fixes simply to get around issues.

6. Do NOT make bandaid fixes that break the rearchitecture goals for the library. Always respect the architectural boundaries.

7. **Practice Test-Driven Development (TDD):** Write tests BEFORE implementing features using the red-green-refactor cycle:
   - **Red:** Write a failing test that defines the desired behavior
   - **Green:** Write minimal code to make the test pass
   - **Refactor:** Improve code quality while keeping tests green

   Benefits:
   - Forces clear requirement thinking before coding
   - Ensures all code is testable and tested
   - Creates a safety net for refactoring
   - Documents expected behavior through tests
   - Prevents scope creep and over-engineering

8. All package imports should be at the top of the file, following standard Python conventions. Avoid dynamic imports or imports within functions. Instead, consider refactoring code to allow for static imports. If circular dependencies arise, it's a sign that the code structure may need to be reconsidered.

9. When implementing new features, always create corresponding example files in the `examples/` folder demonstrating usage. Follow existing example patterns (clear docstring, multiple use cases, well-commented code).
