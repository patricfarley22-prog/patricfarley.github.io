#!/usr/bin/env node
/**
 * QUANTUM DAILY ROUTINE
 * Combines scan + tweet generation in one command
 * 
 * Usage: node quantum-daily.mjs
 *        node quantum-daily.mjs --tweet (also generates tweets)
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

async function runScript(script, args = []) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [join(__dirname, script), ...args], {
      stdio: 'inherit'
    });
    proc.on('close', code => {
      if (code === 0) resolve();
      else reject(new Error(`Script ${script} failed`));
    });
  });
}

async function main() {
  console.log('🔮 Quantum Daily Routine\n');
  
  // Step 1: Run quantum scan
  console.log('Step 1: Running quantum scan...');
  console.log('----------------------------------------');
  await runScript('run-quantum-scan.mjs');
  
  // Step 2: Generate tweets
  if (process.argv.includes('--tweet')) {
    console.log('\nStep 2: Generating tweets...');
    console.log('----------------------------------------');
    await runScript('post-quantum-tweet.mjs', ['standard']);
    
    console.log('\nStep 3: Generating thread...');
    console.log('----------------------------------------');
    await runScript('post-quantum-tweet.mjs', ['thread']);
  }
  
  console.log('\n✅ Quantum daily routine complete!');
  console.log('\nFiles generated:');
  console.log('- Scan results: data/quantum-scan-*.json');
  console.log('- Tweet ready: data/latest-tweet.txt');
  console.log('- Thread ready: data/latest-tweet.txt (thread format)');
}

main().catch(console.error);
