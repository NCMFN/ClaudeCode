"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const res = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    if (res?.error) {
      setError("Invalid credentials");
    } else {
      router.push("/admin");
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-ivory">
      <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-md border border-light-grey">
        <h1 className="text-2xl font-serif text-brand-green mb-6 text-center">Admin Login</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-dark-charcoal mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border border-light-grey rounded focus:ring-brand-gold focus:border-brand-gold outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-charcoal mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border border-light-grey rounded focus:ring-brand-gold focus:border-brand-gold outline-none"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-brand-green text-white py-2 rounded hover:bg-opacity-90 transition-colors font-medium"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
