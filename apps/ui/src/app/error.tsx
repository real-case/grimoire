'use client'

/**
 * Error Boundary Component
 *
 * Catches unexpected errors in the application and displays a fallback UI.
 * Provides a retry mechanism for users to attempt recovery.
 *
 * This is a Next.js error boundary that catches errors in the component tree.
 * See: https://nextjs.org/docs/app/building-your-application/routing/error-handling
 */

import { useEffect } from 'react'

// Force dynamic rendering
export const dynamic = 'force-dynamic'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to console in development
    console.error('Application error:', error)

    // TODO: In production, send to error tracking service (e.g., Sentry)
    // Sentry.captureException(error);
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-card border border-border rounded-lg shadow-sm p-8 text-center space-y-6">
        {/* Error Icon */}
        <div className="flex justify-center">
          <svg
            className="w-16 h-16 text-destructive"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        {/* Error Message */}
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-foreground">
            Something went wrong
          </h2>
          <p className="text-muted-foreground">
            {error.message || 'An unexpected error occurred. Please try again.'}
          </p>
        </div>

        {/* Error Details (Development Only) */}
        {process.env.NODE_ENV === 'development' && error.stack && (
          <details className="text-left">
            <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
              Show error details
            </summary>
            <pre className="mt-2 text-xs bg-muted p-3 rounded overflow-auto max-h-40">
              {error.stack}
            </pre>
          </details>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={reset}
            className="flex-1 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
          <a
            href="/"
            className="flex-1 px-6 py-3 border border-border text-foreground rounded-lg font-medium hover:bg-muted transition-colors text-center"
          >
            Go Home
          </a>
        </div>

        {/* Error Digest (if available) */}
        {error.digest && (
          <p className="text-xs text-muted-foreground">
            Error ID: {error.digest}
          </p>
        )}
      </div>
    </div>
  )
}
