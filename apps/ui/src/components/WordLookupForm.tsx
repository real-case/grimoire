'use client'

/**
 * Word Lookup Form Component
 *
 * Provides a text input for word lookup with validation and loading states.
 * Supports Unicode input (diacritics, non-English characters) per FR-012.
 */

import { useState, FormEvent } from 'react'

export interface WordLookupFormProps {
  onSubmit: (word: string) => void
  onRetry?: () => void
  isLoading?: boolean
  error?: string | null
  retryable?: boolean
}

export default function WordLookupForm({
  onSubmit,
  onRetry,
  isLoading = false,
  error = null,
  retryable = false,
}: WordLookupFormProps) {
  const [word, setWord] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()

    // Clear previous validation error
    setValidationError(null)

    // Validate input
    const trimmedWord = word.trim()
    if (trimmedWord.length === 0) {
      setValidationError('Please enter a word')
      return
    }

    // Submit the word
    onSubmit(trimmedWord)
  }

  const handleInputChange = (value: string) => {
    setWord(value)
    // Clear validation error when user starts typing
    if (validationError) {
      setValidationError(null)
    }
  }

  const showError = validationError || error

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex flex-col gap-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={word}
            onChange={(e) => handleInputChange(e.target.value)}
            placeholder="Enter a word..."
            disabled={isLoading}
            className={`flex-1 px-4 py-3 rounded-lg border ${
              showError
                ? 'border-destructive focus:ring-destructive'
                : 'border-input focus:ring-ring'
            } focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed`}
            aria-label="Word to look up"
            aria-invalid={!!showError}
            aria-describedby={showError ? 'lookup-error' : undefined}
          />
          <button
            type="submit"
            disabled={isLoading || word.trim().length === 0}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Loading...
              </span>
            ) : (
              'Search'
            )}
          </button>
        </div>
        {showError && (
          <div id="lookup-error" className="space-y-2" role="alert">
            <p className="text-sm text-destructive">{showError}</p>
            {retryable && onRetry && error && (
              <div className="flex items-center gap-2">
                <p className="text-xs text-muted-foreground">
                  This error is temporary. You can try again.
                </p>
                <button
                  onClick={onRetry}
                  type="button"
                  className="text-xs text-primary hover:underline font-medium"
                >
                  Retry now
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </form>
  )
}
