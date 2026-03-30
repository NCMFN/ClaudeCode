# User Profile Intake Guide

## When to Use

- You are gathering profile information for a brand-new `user.md`
- You are updating `user.md` and need to know which questions still matter
- You want a lightweight intake flow that stays conversational instead of turning into a questionnaire

## How It Works

1. Start with role, because it unlocks the best follow-up questions
2. Gather up to five anchor fields, but omit fields that do not apply
3. Collect Context opportunistically instead of interrogating the user
4. Keep the final output short enough to stay useful in prompt context

## Examples

- A technical user where Role, Stack, Style, and Timezone are known
- A non-technical user where Stack is omitted entirely
- A quick refresh where only Role and current goals changed

## Goal

Produce a user.md under 500 words: up to 5 anchor fields + a natural-language Context section.

## Anchor Fields (structured — for precise extraction)

| Field | Purpose | How to gather |
|-------|---------|---------------|
| Name | What the user wants to be called | Ask directly, or pick it up from conversation |
| Role | Job title or identity — drives recommendations and interaction style | "What do you do for a living?" |
| Stack | Core tech stack (omit for non-technical roles) | "What's in your toolbox day to day?" |
| Style | Communication preference | "Do you like your lobster concise or thorough?" |
| Timezone | Timezone | Infer from system info, then confirm |

## Context Section (natural language — gathered progressively)

The following info is **not** captured as standalone fields. Instead, it's **woven into the Context section as natural prose**. Record it when it comes up; don't chase it down:

| Info | When to collect | How |
|------|----------------|-----|
| Industry / domain | Comes up naturally when discussing role | Infer from role, or ask casually |
| Experience level | Comes up naturally when discussing stack | "How long have you been at it?" or infer from tone |
| Current goals | When the user mentions them | "What are you working on these days?" |
| Use cases | When discussing why they use an Agent | "What do you mainly want your lobster helping with?" |
| Habits / preferences | Observed during interaction | Don't ask — just notice and note |
| Interests | When it comes up naturally | Don't push |
| Pain points | When the user volunteers them | Don't push |

## Intake Principles

1. **Chat, don't interview**: one or two questions at a time — never a checklist
2. **Role first**: once you know the role, a lot of other info can be inferred — engineers probably have a stack, CEOs care about strategy
3. **Confirm, don't interrogate**: if you can guess, say "I'm guessing you work with [X]?" and let them correct you
4. **Two rounds is enough**: 2–3 conversational turns should cover the anchor fields + baseline Context
5. **Context is opportunistic**: don't press for details just to fill space — if it comes up, write it down; if it doesn't, leave it for next time
6. **500-word hard cap**: check the total word count after writing — if it's over, trim; better to say less than to pad
