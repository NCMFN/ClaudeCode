# ACTEN Nigeria Official Website

This repository contains the source code for the official website of ACTEN — the Association of Catholic Trained Evangelizers in Nigeria.

## Features

*   **Responsive Design:** Fully responsive layout using Tailwind CSS.
*   **Content Management:** Admin dashboard to manage articles, events, and reports.
*   **Report Submissions:** Allows visitors to submit diocesan reports for review.
*   **Authentication:** Secured admin area using NextAuth.js.
*   **Database:** PostgreSQL integration via Prisma ORM.

## Tech Stack

*   [Next.js](https://nextjs.org/) (App Router)
*   [React](https://react.dev/)
*   [TypeScript](https://www.typescriptlang.org/)
*   [Tailwind CSS](https://tailwindcss.com/)
*   [Prisma](https://www.prisma.io/)
*   [NextAuth.js](https://next-auth.js.org/)
*   [PostgreSQL](https://www.postgresql.org/)

## Local Development Setup

### Prerequisites

*   Node.js (v18+)
*   Docker (for running the local PostgreSQL database)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd acten-website
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Environment Variables:**
    Create a `.env` file in the root of the `acten-website` directory based on the `.env.example` file:
    ```bash
    cp .env.example .env
    ```
    Ensure the `DATABASE_URL` matches your local database setup.

4.  **Database Setup:**
    Start a local PostgreSQL instance. If using Docker:
    ```bash
    docker run --name acten-db -e POSTGRES_PASSWORD=acten -e POSTGRES_DB=acten -p 5432:5432 -d postgres:alpine
    ```

    Push the Prisma schema to the database:
    ```bash
    npx prisma db push
    ```

5.  **Create Initial Admin User:**
    To access the admin dashboard, create an initial super admin user:
    ```bash
    npx ts-node scripts/create-admin.ts
    ```
    *Note: The default credentials are `admin@acten.ng` and password `password123`. Please change these in a production environment.*

6.  **Run the Development Server:**
    ```bash
    npm run dev &
    ```
    Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Deployment

The application can be deployed easily to Vercel:

1. Push your code to a GitHub repository.
2. Import the project into Vercel.
3. Add the environment variables (`DATABASE_URL`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`) in the Vercel dashboard.
4. Deploy!

Ensure that your production database (e.g., Supabase, Neon) is properly configured and accessible.

## Project Structure

*   `src/app`: Contains all Next.js routes (pages, layouts, api).
*   `src/components`: Reusable React components.
*   `src/lib`: Utility functions and Prisma client setup.
*   `prisma`: Prisma schema and migrations.
*   `scripts`: Utility scripts (e.g., for creating an admin user).
