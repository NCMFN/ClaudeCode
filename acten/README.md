# ACTEN Official Website

The official website for the **Association of Catholic Trained Evangelizers in Nigeria (ACTEN)**.
Proclaiming Christ. Sharing the Gospel. Serving Communities.

## Tech Stack
- Next.js (App Router)
- React & TypeScript
- Tailwind CSS
- Prisma ORM (SQLite for local, switch to PostgreSQL for production)
- NextAuth.js (Credentials Provider with bcrypt)

## Setup Instructions

1. **Install dependencies:**
   `npm install`

2. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in the values:
   `cp .env.example .env`

3. **Database Setup (Local):**
   This project uses SQLite for local development. Run the following to push the schema:
   `npx prisma db push`

4. **Run Development Server:**
   `npm run start-dev`
   Open http://localhost:3000 with your browser.

## Deployment to Vercel (Production)
For production, it's recommended to use PostgreSQL (e.g., via Supabase or Vercel Postgres).

1. Change the Prisma provider in `prisma/schema.prisma` from `"sqlite"` to `"postgresql"`.
2. Update the `DATABASE_URL` in your Vercel project's Environment Variables.
3. Deploy via Vercel GitHub integration or CLI.
4. Configure NextAuth settings (`NEXTAUTH_URL`, `NEXTAUTH_SECRET`) in Vercel.

## Secure Admin Setup
By default, there are no admin accounts. You must create the initial Super Administrator by interacting with the database directly or creating a secure seeder script.
Never commit default credentials to the repository.
