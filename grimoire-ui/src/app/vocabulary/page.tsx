'use client'

/**
 * Vocabulary List Page
 *
 * Displays saved vocabulary entries with pagination and sorting.
 */

import { useEffect, useState } from 'react'
import { useVocabulary } from '@/hooks/useVocabulary'
import VocabularyList from '@/components/VocabularyList'
import Link from 'next/link'

export default function VocabularyPage() {
  const { entries, pagination, isLoading, error, fetchVocabulary } = useVocabulary()
  const [sortBy, setSortBy] = useState<'savedAt' | 'lastModified' | 'word'>('lastModified')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    fetchVocabulary({ sortBy, order })
  }, [fetchVocabulary, sortBy, order])

  const handlePageChange = (page: number) => {
    fetchVocabulary({ page, sortBy, order })
  }

  const handleSortChange = (newSortBy: 'savedAt' | 'lastModified' | 'word', newOrder: 'asc' | 'desc') => {
    setSortBy(newSortBy)
    setOrder(newOrder)
  }

  return (
    <main className="min-h-screen p-8 md:p-24">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground">
              My Vocabulary
            </h1>
            <p className="text-muted-foreground text-lg mt-2">
              {pagination ? `${pagination.total} saved words` : 'Your saved words'}
            </p>
          </div>
          <Link
            href="/"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
          >
            ← Back to Search
          </Link>
        </div>

        {/* Sort Controls */}
        <div className="flex gap-4 items-center">
          <span className="text-sm text-muted-foreground">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => handleSortChange(e.target.value as any, order)}
            className="px-3 py-2 border border-border rounded-lg bg-background"
          >
            <option value="lastModified">Last Modified</option>
            <option value="savedAt">Date Saved</option>
            <option value="word">Word (A-Z)</option>
          </select>
          <button
            onClick={() => handleSortChange(sortBy, order === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-2 border border-border rounded-lg hover:bg-accent"
          >
            {order === 'asc' ? '↑ Ascending' : '↓ Descending'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-destructive/10 border border-destructive text-destructive rounded-lg p-4">
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-16">
            <div className="inline-block animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
            <p className="text-muted-foreground mt-4">Loading vocabulary...</p>
          </div>
        )}

        {/* Vocabulary List */}
        {!isLoading && pagination && (
          <VocabularyList
            entries={entries}
            pagination={pagination}
            onPageChange={handlePageChange}
            onSortChange={handleSortChange}
          />
        )}
      </div>
    </main>
  )
}
