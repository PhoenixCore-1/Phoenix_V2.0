import { test, expect } from '@playwright/test'

const username = process.env.PHOENIX_E2E_USERNAME
const password = process.env.PHOENIX_E2E_PASSWORD


test.describe('Phoenix Company Platform - VPS browser gate', () => {
  test.skip(!username || !password, 'Set PHOENIX_E2E_USERNAME and PHOENIX_E2E_PASSWORD for the authenticated VPS gate.')

  test('logs in through Core and reaches the Company Platform', async ({ page }) => {
    await page.goto('/company')

    await expect(page).toHaveTitle(/Phoenix/i)

    const usernameInput = page.getByLabel(/username/i)
    const passwordInput = page.getByLabel(/password/i)

    await expect(usernameInput).toBeVisible()
    await expect(passwordInput).toBeVisible()

    await usernameInput.fill(username!)
    await passwordInput.fill(password!)
    await page.getByRole('button', { name: /sign in|login/i }).click()

    await expect(page.getByText(/Company Platform/i).first()).toBeVisible({ timeout: 15_000 })

    const expectedWorkspaces = [
      /Dashboard/i,
      /People/i,
      /Workspaces/i,
      /Visibility/i,
      /Activity/i,
      /Reports/i,
      /Settings/i,
      /Connect/i,
    ]

    for (const workspace of expectedWorkspaces) {
      await expect(page.getByText(workspace).first()).toBeVisible()
    }
  })

  test('Core session survives navigation and logout returns to login', async ({ page }) => {
    await page.goto('/company')

    await page.getByLabel(/username/i).fill(username!)
    await page.getByLabel(/password/i).fill(password!)
    await page.getByRole('button', { name: /sign in|login/i }).click()

    await expect(page.getByText(/Company Platform/i).first()).toBeVisible({ timeout: 15_000 })

    await page.reload()
    await expect(page.getByText(/Company Platform/i).first()).toBeVisible({ timeout: 15_000 })

    const logout = page.getByRole('button', { name: /logout|sign out/i })
    await expect(logout).toBeVisible()
    await logout.click()

    await expect(page.getByLabel(/username/i)).toBeVisible({ timeout: 10_000 })
    await expect(page.getByLabel(/password/i)).toBeVisible()
  })
})
