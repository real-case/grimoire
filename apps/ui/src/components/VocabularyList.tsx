'use client'

/**
 * Vocabulary List Component
 *
 * Displays saved vocabulary entries with pagination, sorting, and filtering.
 */

import type { VocabularyListItem, Pagination } from '@/types/contracts'

export interface VocabularyListProps {
  entries: VocabularyListItem[]
  pagination: Pagination
  onPageChange: (page: number) => void
  onSortChange: (sortBy: 'savedAt' | 'lastModified' | 'word', order: 'asc' | 'desc') => void
  className?: string
}

export default function VocabularyList({
  entries,
  pagination,
  onPageChange,
  onSortChange,
  className = '',
}: VocabularyListProps) {
  if (entries.length === 0) {
    return (
      <div className={`text-center py-16 ${className}`}>
        <p className="text-muted-foreground text-lg">No saved words yet</p>
        <p className="text-sm text-muted-foreground mt-2">
          Look up and save words to build your vocabulary collection
        </p>
      </div>
    )
  }

  return (
    <div className={`w-full ${className}`}>
      {/* List */}
      <div className="space-y-4">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="bg-card border border-border rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-foreground capitalize mb-2">
                  {entry.word}
                </h3>
                <p className="text-muted-foreground line-clamp-2">{entry.preview}</p>
                {entry.tags && entry.tags.length > 0 && (
                  <div className="flex gap-2 mt-3">
                    {entry.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-accent text-accent-foreground rounded-full text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="ml-4 text-sm text-muted-foreground text-right">
                <p>Saved: {new Date(entry.savedAt).toLocaleDateString()}</p>
                {entry.hasCustomEdits && (
                  <p className="text-primary mt-1">● Edited</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="mt-8 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {pagination.page * pagination.limit + 1} to{' '}
            {Math.min((pagination.page + 1) * pagination.limit, pagination.total)} of{' '}
            {pagination.total} words
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(pagination.page - 1)}
              disabled={!pagination.hasPrevious}
              className="px-4 py-2 border border-border rounded-lg hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => onPageChange(pagination.page + 1)}
              disabled={!pagination.hasNext}
              className="px-4 py-2 border border-border rounded-lg hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
