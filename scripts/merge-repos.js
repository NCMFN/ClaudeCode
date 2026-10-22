#!/usr/bin/env node

const { execSync } = require('child_process');

const repositories = [
    { name: 'gan_project', remote: 'gan_project' },
    { name: 'humai', remote: 'humai' },
    { name: 'Dokhac', remote: 'Dokhac' },
    { name: 'NoeFabris', remote: 'NoeFabris' }
];

try {
    // Step 1: Add remotes
    repositories.forEach(repo => {
        console.log(`Adding remote for ${repo.name}...`);
        execSync(`git remote add ${repo.remote} https://github.com/NCMFN/${repo.name}.git`, { stdio: 'inherit' });
    });

    // Step 2: Fetch all remotes
    console.log('Fetching all remotes...');
    execSync('git fetch --all', { stdio: 'inherit' });

    // Step 3: Merge each repository using subtree strategy
    repositories.forEach(repo => {
        console.log(`Merging ${repo.name} using subtree strategy...`);
        execSync(`git merge ${repo.remote}/main --squash --allow-unrelated-histories`, { stdio: 'inherit' });
    });

    // Step 4: Push changes to main branch
    console.log('Pushing changes to main branch...');
    execSync('git push origin main', { stdio: 'inherit' });

    // Step 5: Display merge summary results
    console.log('Merge completed successfully.');
} catch (error) {
    console.error('An error occurred:', error.message);
    process.exit(1);
}