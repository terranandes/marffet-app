import { test, expect } from '@playwright/test';

test.describe('Mobile Portfolio Card View', () => {
    test.use({ viewport: { width: 390, height: 844 } }); // iPhone 12

    test('Guest Mode - Mobile Card View Verification', async ({ page }) => {
        // 1. Login as Guest
        await page.goto('/');
        // Check if login overlay is present (Legacy UI might show it, Next.js might redirect)
        // For Next.js app, we might need to click "Continue as Guest" if it's the landing page
        // or if we are redirected to /auth/login

        // Attempt to handle landing page "Continue as Guest" if present
        const guestBtn = page.getByRole('button', { name: 'Continue as Guest' });
        if (await guestBtn.isVisible()) {
            await guestBtn.click();
        }

        // Navigate to Portfolio
        await page.goto('/portfolio');

        // Handle "Continue as Guest" if shown on Portfolio page (Next.js sync)
        const guestBtn2 = page.getByRole('button', { name: 'Continue as Guest' });
        if (await guestBtn2.isVisible()) {
            await guestBtn2.click();
        }

        // Ensure we are on Portfolio page
        await expect(page).toHaveURL(/.*portfolio/);

        // 2. Create a Group if none exists (Guest Mode starts empty usually)
        // Check for "No groups yet" or "Start Your Portfolio"
        const startMsg = page.getByText('Start Your Portfolio');
        if (await startMsg.isVisible()) {
            await page.getByRole('button', { name: '+ New Group' }).click();
            await page.getByPlaceholder('Group name...').fill('Mobile Test Group');
            await page.getByRole('button', { name: 'Create' }).click();
        }

        // 3. Add a Target
        await page.getByPlaceholder('Stock ID (e.g. 2330)').fill('2330');
        // Name might be auto-fetched or manual
        await page.getByPlaceholder('Name (e.g. 台積電)').fill('TSMC');
        await page.getByRole('button', { name: '+ Add Stock' }).click();

        // 4. Verify Layout
        // Table should be hidden
        const tableContainer = page.locator('table').first();
        // In our implementation, the table container div has 'hidden lg:block'
        // We can check if the table is visible. 
        // Note: Locator points to elements. If the parent div is hidden, the table is not visible.
        await expect(tableContainer).toBeHidden();

        // Cards should be visible
        // We look for the stock name in the card header
        const stockCard = page.getByText('TSMC').first();
        await expect(stockCard).toBeVisible();

        // 5. Interact (Expand)
        // Check if details are initially hidden (e.g., "Shares")
        // "Shares" label is in the expanded details
        const sharesLabel = page.getByText('Shares', { exact: true });
        await expect(sharesLabel).toBeHidden();

        // Click to expand
        await stockCard.click();

        // Verify Details correspond to expansion
        await expect(sharesLabel).toBeVisible();

        // Verify Action Buttons
        await expect(page.getByRole('button', { name: '➕ Add Tx' })).toBeVisible();
        await expect(page.getByRole('button', { name: '📜 History' })).toBeVisible();
        await expect(page.getByRole('button', { name: '🗑️' })).toBeVisible();

        // 6. Test Card Action (Add Tx)
        await page.getByRole('button', { name: '➕ Add Tx' }).click();
        await expect(page.getByText('New Transaction')).toBeVisible();
        // Close modal
        await page.getByRole('button', { name: 'Cancel' }).click();
    });
});
