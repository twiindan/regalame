# Regalame project

## Project Overview

This is a full-stack project using FastAPI for the backend and React for the frontend. The project is set up to use Docker Compose for development and production, which makes it easy to get started.

The backend is a FastAPI application that uses SQLModel as an ORM to interact with a PostgreSQL database. It includes features like secure password hashing, JWT authentication, and email-based password recovery.

The frontend is a React application built with Vite. It uses Shadcn UI for components and has an automatically generated frontend client.

Traefik is used as a reverse proxy to handle routing traffic to the correct service.

## Building and Running

To build and run the project, you will need to have Docker and Docker Compose installed.

1.  **Start the development environment:**

    ```bash
    docker compose watch
    ```

2.  **Access the application:**

    *   **Frontend:** [http://localhost:5173](http://localhost:5173)
    *   **Backend:** [http://localhost:8000](http://localhost:8000)
    *   **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **Adminer (Database Admin):** [http://localhost:8080](http://localhost:8080)

## Development Conventions

### Backend

The backend code is located in the `backend/` directory. It follows standard FastAPI project structure.

*   **Dependencies:** Backend dependencies are managed with `uv` and are listed in `backend/pyproject.toml`. To install them, run:
    ```bash
    uv sync
    ```
*   **Tests:** Tests are written with Pytest and are located in the `backend/tests/` directory. To run the tests, you can use the following command:

    ```bash
    bash ./scripts/test.sh
    ```
*   **Database Migrations:** Database migrations are handled with Alembic. To create a new migration, run:
    ```bash
    docker compose exec backend alembic revision --autogenerate -m "Your migration message"
    ```
    To apply the migrations, run:
    ```bash
    docker compose exec backend alembic upgrade head
    ```

### Frontend

The frontend code is located in the `frontend/` directory.

*   **Dependencies:** Frontend dependencies are managed with npm and are listed in `frontend/package.json`. To install them, run:
    ```bash
    npm install
    ```
*   **Development Server:** To start the frontend development server, run:
    ```bash
    npm run dev
    ```
*   **Tests:** End-to-end tests are written with Playwright and are located in the `frontend/tests/` directory. To run the tests, first start the backend with `docker compose up -d --wait backend` and then run:
    ```bash
    npx playwright test
    ```
*   **Generate API Client:** To generate the frontend API client, run:
    ```bash
    ./scripts/generate-client.sh
    ```
### shadcn/ui Configuration

- Style: "new-york"
- Base color: zinc
- CSS variables enabled for theming
- Components auto-imported to `@/components/ui`

### Adding Frontend Components

Use shadcn/ui CLI:
```bash
npx shadcn-ui@latest add [component-name]
```

### Linting and Formatting

This project uses pre-commit to enforce code style and formatting.

*   **Backend:** The backend uses `ruff` for linting and formatting.
*   **Frontend:** The frontend uses `biome` for linting and formatting.

To install the pre-commit hooks, run:

```bash
uv run pre-commit install
```

## Deployment

This project is designed to be deployed with Docker Compose. For detailed instructions on how to deploy the application, please see the [deployment.md](deployment.md) file.


## Code Writing Standards

- **Simplicity First**: Prefer simple, clean, maintainable solutions over clever ones
- **ABOUTME Comments**: All files must start with 2-line comment with "ABOUTME: " prefix
- **Minimal Changes**: Make smallest reasonable changes to achieve desired outcome
- **Style Matching**: Match existing code style/formatting within each file
- **Preserve Comments**: Never remove comments unless provably false
- **No Temporal Naming**: Avoid 'new', 'improved', 'enhanced', 'recently' in names/comments
- **Evergreen Documentation**: Comments describe code as it is, not its history

## Version Control

- Non-trivial edits must be tracked in git
- Create WIP branches for new work
- Commit frequently throughout development
- Never throw away implementations without explicit permission


## Testing Requirements

**NO EXCEPTIONS POLICY**: All projects MUST have:
- Unit tests

The only way to skip tests: Toni EXPLICITLY states "I AUTHORIZE YOU TO SKIP WRITING TESTS THIS TIME."

- Tests must comprehensively cover all functionality
- Test output must be pristine to pass
- Never ignore system/test output - logs contain critical information


When writing frontend code:

1. **Container Pattern**: Separate business logic from presentation
2. **Custom Hooks**: Business logic in hooks (e.g., `useConversation`)
3. **Feature Organization**: Group by feature in `app/features/`
4. **Component Purity**: Components receive props, hooks manage state


## Code Writing

- YOU MUST ALWAYS address me as "Toni" in all communications.
- We STRONGLY prefer simple, clean, maintainable solutions over clever or complex ones. Readability and maintainability are PRIMARY CONCERNS, even at the cost of conciseness or performance.
- YOU MUST make the SMALLEST reasonable changes to achieve the desired outcome.
- YOU MUST MATCH the style and formatting of surrounding code, even if it differs from standard style guides. Consistency within a file trumps external standards.
- YOU MUST NEVER make code changes unrelated to your current task. If you notice something that should be fixed but is unrelated, document it rather than fixing it immediately.
- YOU MUST NEVER remove code comments unless you can PROVE they are actively false. Comments are important documentation and must be preserved.
- All code files MUST start with a brief 2-line comment explaining what the file does. Each line MUST start with "ABOUTME: " to make them easily greppable.
- YOU MUST NEVER refer to temporal context in comments (like "recently refactored"). Comments should be evergreen and describe the code as it is.
- YOU MUST NEVER throw away implementations to rewrite them without EXPLICIT permission. If you're considering this, YOU MUST STOP and ask first.
- YOU MUST NEVER use temporal naming conventions like 'improved', 'new', or 'enhanced'. All naming should be evergreen.
- YOU MUST NOT change whitespace unrelated to code you're modifying.

## Getting Help

- Always ask for clarification rather than making assumptions
- Stop and ask for help when stuck, especially when human input would be valuable
- If considering an exception to any rule, stop and get explicit permission from Fran first

## Testing

- Tests MUST comprehensively cover ALL implemented functionality. 
- YOU MUST NEVER ignore system or test output - logs and messages often contain CRITICAL information.
- Test output MUST BE PRISTINE TO PASS.
- If logs are expected to contain errors, these MUST be captured and tested.
- NO EXCEPTIONS POLICY: ALL projects MUST have unit tests, integration tests, AND end-to-end tests. The only way to skip any test type is if Toni EXPLICITLY states: "I AUTHORIZE YOU TO SKIP WRITING TESTS THIS TIME."


## Compliance Check
Before submitting any work, verify that you have followed ALL guidelines above. If you find yourself considering an exception to ANY rule, YOU MUST STOP and get explicit permission from Toni first.
