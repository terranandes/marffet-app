import { test, expect } from '@playwright/test';

test('Home page translates i18n keys properly', async ({ page }) => {
  await page.goto('http://127.0.0.1:8000');
  
  // Wait for content
  await page.waitForLoadState('networkidle');
  
  // Verify standard English text instead of raw keys
  await expect(page.locator('h1')).toContainText('Investment Intelligence');
  await expect(page.locator('body')).not.toContainText('Home.MarsStrategy');
  await expect(page.locator('body')).toContainText('Mars Strategy');
  
  // Switch to Traditional Chinese
  await page.goto('http://127.0.0.1:8000/settings');
  await page.getByRole('tab', { name: 'Preferences' }).click();
  await page.getByRole('combobox').filter({ hasText: 'Language' }).selectOption('zh-TW');
  await page.getByRole('button', { name: 'Save Preferences' }).click();
  
  // Go back home
  await page.goto('http://127.0.0.1:8000');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('h1')).toContainText('投資情報中心');
});
