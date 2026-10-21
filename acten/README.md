# ACTEN - Association of Catholic Trained Evangelizers in Nigeria

This is the official web application for the Association of Catholic Trained Evangelizers in Nigeria (ACTEN). It provides a digital platform for documenting, publishing, and promoting Catholic evangelization activities across the country.

## Architecture & Tech Stack

- **Frontend:** Next.js (App Router), React, TypeScript
- **Styling:** Tailwind CSS
- **Components:** Radix UI, Lucide React
- **Database:** PostgreSQL
- **ORM:** Prisma
- **Authentication:** NextAuth.js (Credentials Provider)

## Getting Started

### Prerequisites
- Node.js (v18+)
- PostgreSQL Database

### Installation

1. Install dependencies:
   `npm install`

2. Set up environment variables:
   Copy `.env.example` to `.env` and configure your database URL and NextAuth secret.
   `DATABASE_URL="postgresql://user:password@localhost:5432/acten?schema=public"`
   `NEXTAUTH_SECRET="your-super-secret-key"`
   `NEXTAUTH_URL="http://localhost:3000"`

3. Initialize the database:
   `npx prisma generate`
   `npx prisma db push`

4. Start the development server:
   `npm run dev`

## Development Workflow

- The public site includes sections for News, Events, Resources, Reports, Gallery, and Contact.
- Visitors can submit evangelization reports via `/submit`.
- Administrators can manage content via the `/admin` dashboard.
- Submissions start with a `PENDING` status and require editorial approval.

## Deployment

The project is ready to be deployed to platforms like Vercel or any Node.js environment. Ensure you configure environment variables for production and run `npx prisma deploy` or `npx prisma db push` against the production database.
