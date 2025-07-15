#!/usr/bin/env node

/**
 * Conditional Husky Installation Script
 * Only installs husky git hooks in development environments
 * Skips installation in CI/CD environments like Render, Vercel, etc.
 */

const fs = require('fs');
const path = require('path');

// Check if we're in a CI environment
const isCI = process.env.CI || 
             process.env.RENDER || 
             process.env.VERCEL || 
             process.env.NETLIFY ||
             process.env.GITHUB_ACTIONS ||
             process.env.NODE_ENV === 'production';

// Check if .git directory exists (indicates a git repository)
const gitExists = fs.existsSync(path.join(process.cwd(), '.git'));

// Only install husky if we're in development and have git
if (!isCI && gitExists) {
  try {
    const husky = require('husky');
    husky.install();
    console.log('✅ Husky git hooks installed successfully');
  } catch (error) {
    if (error.code === 'MODULE_NOT_FOUND') {
      console.log('⚠️ Husky not found, skipping git hooks setup');
    } else {
      console.warn('⚠️ Failed to install husky:', error.message);
    }
  }
} else {
  if (isCI) {
    console.log('⏭️ Skipping husky installation in CI environment');
  } else if (!gitExists) {
    console.log('⏭️ Skipping husky installation - no git repository detected');
  }
}