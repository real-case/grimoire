'use client'

import { useState } from 'react'
import { useWordLookup } from '@/hooks/useWordLookup'
import { useVocabulary } from '@/hooks/useVocabulary'
import WordLookupForm from '@/components/WordLookupForm'
import WordDisplay from '@/components/WordDisplay'
import Link from 'next/link'

// Force dynamic rendering to avoid pre-rendering errors with client-side hooks
export const dynamic = 'force-dynamic'

export default function Home() {
  const { wordData, isLoading, error, retryable, lookupWord, retry } = useWordLookup()
  const { saveWord } = useVocabulary()
  const [isSaving, setIsSaving] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  const handleSave = async (customFields?: any) => {
    if (!wordData) return

    setIsSaving(true)
    setSaveMessage(null)

    const success = await saveWord({
      word: wordData.word,
      originalData: wordData,
      ...customFields,
    })

    setIsSaving(false)
    if (success) {
      setIsSaved(true)
      setSaveMessage('Word saved successfully!')
      setTimeout(() => setSaveMessage(null), 3000)
    }
  }

  const handleNewSearch = () => {
    setIsSaved(false)
    setSaveMessage(null)
  }

  return (
    <main className="min-h-screen p-8 md:p-24">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Grimoire
          </h1>
          <p className="text-muted-foreground text-lg">
            Build your personal vocabulary collection
          </p>
        </div>

        {/* Navigation */}
        <div className="flex justify-end">
          <Link
            href="/vocabulary"
            className="px-4 py-2 text-primary hover:underline"
          >
            View Saved Words →
          </Link>
        </div>

        {/* Search Form */}
        <WordLookupForm
          onSubmit={(word) => {
            handleNewSearch()
            lookupWord(word)
          }}
          onRetry={retry}
          isLoading={isLoading}
          error={error}
          retryable={retryable}
        />

        {/* Save Success Message */}
        {saveMessage && (
          <div className="bg-secondary border border-border rounded-lg p-4 text-center">
            <p className="text-foreground">{saveMessage}</p>
          </div>
        )}

        {/* Results */}
        {wordData && !isLoading && (
          <div className="mt-8">
            <WordDisplay
              wordData={wordData}
              onSave={handleSave}
              isSaving={isSaving}
              isSaved={isSaved}
            />
          </div>
        )}

        {/* Empty state */}
        {!wordData && !isLoading && !error && (
          <div className="text-center py-16">
            <p className="text-muted-foreground">
              Enter a word above to get started
            </p>
          </div>
        )}
      </div>
    </main>
  )
}
