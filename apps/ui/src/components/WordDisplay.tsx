'use client'

/**
 * Word Display Component
 *
 * Displays comprehensive word information from the API with editing capabilities.
 * Shows "Not available" for missing fields (FR-013).
 * Uses scrollable containers for long content (FR-003).
 * Supports inline editing with React Hook Form (US2).
 */

import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import type { EnhancedWordData } from '@/types/contracts'
import EditableField from './EditableField'

export interface WordDisplayProps {
  wordData: EnhancedWordData
  onSave?: (customFields?: CustomFields) => void
  isSaving?: boolean
  isSaved?: boolean
  className?: string
  enableEditing?: boolean
}

export interface CustomFields {
  customDefinition?: string
  customPronunciation?: string
  customExamples?: string[]
  customNotes?: string
  customSynonyms?: string[]
  customAntonyms?: string[]
  customTags?: string[]
}

interface FormData {
  customDefinition: string
  customPronunciation: string
  customExamples: string // Comma-separated
  customNotes: string
  customSynonyms: string // Comma-separated
  customAntonyms: string // Comma-separated
  customTags: string // Comma-separated
}

export default function WordDisplay({
  wordData,
  onSave,
  isSaving = false,
  isSaved = false,
  className = '',
  enableEditing = true,
}: WordDisplayProps) {
  // Initialize React Hook Form with default values from API
  const {
    register,
    handleSubmit,
    formState: { isDirty, dirtyFields },
    reset,
    getValues,
  } = useForm<FormData>({
    defaultValues: {
      customDefinition: '',
      customPronunciation: '',
      customExamples: '',
      customNotes: '',
      customSynonyms: '',
      customAntonyms: '',
      customTags: '',
    },
  })

  // Reset form when word data changes
  useEffect(() => {
    reset({
      customDefinition: '',
      customPronunciation: '',
      customExamples: '',
      customNotes: '',
      customSynonyms: '',
      customAntonyms: '',
      customTags: '',
    })
  }, [wordData.word, reset])

  // Handle save with custom fields
  const handleSaveWithEdits = () => {
    if (!onSave) return

    const formData = getValues()
    const customFields: CustomFields = {
      customDefinition: formData.customDefinition || undefined,
      customPronunciation: formData.customPronunciation || undefined,
      customExamples: formData.customExamples
        ? formData.customExamples.split(',').map(s => s.trim()).filter(Boolean)
        : undefined,
      customNotes: formData.customNotes || undefined,
      customSynonyms: formData.customSynonyms
        ? formData.customSynonyms.split(',').map(s => s.trim()).filter(Boolean)
        : undefined,
      customAntonyms: formData.customAntonyms
        ? formData.customAntonyms.split(',').map(s => s.trim()).filter(Boolean)
        : undefined,
      customTags: formData.customTags
        ? formData.customTags.split(',').map(s => s.trim().toLowerCase()).filter(Boolean)
        : undefined,
    }

    onSave(customFields)
  }

  // Handle discard changes
  const handleDiscardChanges = () => {
    if (confirm('Are you sure you want to discard your changes?')) {
      reset()
    }
  }

  // Warn about unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault()
        e.returnValue = 'You have unsaved changes. Do you want to leave?'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [isDirty])
  return (
    <div className={`w-full max-w-4xl mx-auto ${className}`}>
      <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
        {/* Header */}
        <div className="bg-muted px-6 py-4 border-b border-border">
          <h2 className="text-3xl font-bold text-foreground capitalize">
            {wordData.word}
          </h2>
          {wordData.phonetics && wordData.phonetics.length > 0 && (
            <div className="mt-2 flex flex-wrap items-center gap-4">
              {wordData.phonetics.map((phonetic, index) => (
                <div key={index} className="flex items-center gap-2">
                  {phonetic.text && (
                    <span className="text-muted-foreground">
                      {phonetic.text}
                    </span>
                  )}
                  {phonetic.audio && (
                    <button
                      onClick={() => {
                        const audio = new Audio(phonetic.audio)
                        audio.play()
                      }}
                      className="text-primary hover:text-primary/80 transition-colors"
                      aria-label="Play pronunciation"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Save/Action Buttons */}
        {onSave && (
          <div className="px-6 py-4 border-b border-border">
            <div className="flex gap-3">
              <button
                onClick={handleSaveWithEdits}
                disabled={isSaving || isSaved}
                className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                  isSaved
                    ? 'bg-secondary text-secondary-foreground cursor-default'
                    : 'bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {isSaving ? (
                  <span className="flex items-center justify-center gap-2">
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
                    Saving...
                  </span>
                ) : isSaved ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Saved to Vocabulary
                  </span>
                ) : (
                  'Save to Vocabulary'
                )}
              </button>
              {isDirty && !isSaved && (
                <button
                  onClick={handleDiscardChanges}
                  disabled={isSaving}
                  className="px-6 py-3 rounded-lg font-medium border border-border text-foreground hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Discard Changes
                </button>
              )}
            </div>
            {isDirty && !isSaved && (
              <p className="mt-2 text-sm text-amber-600 dark:text-amber-500">
                You have unsaved changes
              </p>
            )}
          </div>
        )}

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[600px] overflow-y-auto">
          {/* Meanings */}
          {wordData.meanings && wordData.meanings.length > 0 ? (
            wordData.meanings.map((meaning, meaningIndex) => (
              <div key={meaningIndex} className="space-y-3">
                <h3 className="text-lg font-semibold text-primary capitalize">
                  {meaning.partOfSpeech}
                </h3>
                {meaning.definitions && meaning.definitions.length > 0 && (
                  <ol className="space-y-3 list-decimal list-inside">
                    {meaning.definitions.map((def, defIndex) => (
                      <li key={defIndex} className="text-foreground">
                        <span className="ml-2">{def.definition}</span>
                        {def.example && (
                          <p className="mt-1 ml-7 text-sm text-muted-foreground italic">
                            "{def.example}"
                          </p>
                        )}
                        {def.synonyms && def.synonyms.length > 0 && (
                          <p className="mt-1 ml-7 text-sm">
                            <span className="font-medium">Synonyms:</span>{' '}
                            {def.synonyms.join(', ')}
                          </p>
                        )}
                        {def.antonyms && def.antonyms.length > 0 && (
                          <p className="mt-1 ml-7 text-sm">
                            <span className="font-medium">Antonyms:</span>{' '}
                            {def.antonyms.join(', ')}
                          </p>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
                {meaning.synonyms && meaning.synonyms.length > 0 && (
                  <p className="text-sm text-muted-foreground">
                    <span className="font-medium">Synonyms:</span> {meaning.synonyms.join(', ')}
                  </p>
                )}
                {meaning.antonyms && meaning.antonyms.length > 0 && (
                  <p className="text-sm text-muted-foreground">
                    <span className="font-medium">Antonyms:</span> {meaning.antonyms.join(', ')}
                  </p>
                )}
              </div>
            ))
          ) : (
            <p className="text-muted-foreground">Definitions not available</p>
          )}

          {/* Etymology */}
          {wordData.etymology && (
            <div className="border-t border-border pt-4">
              <h3 className="text-lg font-semibold text-foreground mb-2">Etymology</h3>
              <p className="text-muted-foreground">{wordData.etymology}</p>
            </div>
          )}

          {/* Editable Custom Fields Section */}
          {enableEditing && (
            <div className="border-t border-border pt-6 mt-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">
                Personalize This Word
              </h3>
              <p className="text-sm text-muted-foreground mb-6">
                Add your own notes, definitions, and examples. All fields are optional and can be left empty.
              </p>

              <div className="space-y-4">
                <EditableField
                  label="Custom Definition"
                  name="customDefinition"
                  value={getValues('customDefinition')}
                  register={register}
                  type="textarea"
                  placeholder="Add your own simplified definition..."
                  maxLength={2000}
                  isDirty={!!dirtyFields.customDefinition}
                  isEditable={enableEditing}
                />

                <EditableField
                  label="Custom Pronunciation"
                  name="customPronunciation"
                  value={getValues('customPronunciation')}
                  register={register}
                  type="text"
                  placeholder="Add your own pronunciation guide..."
                  maxLength={200}
                  isDirty={!!dirtyFields.customPronunciation}
                  isEditable={enableEditing}
                />

                <EditableField
                  label="Custom Examples"
                  name="customExamples"
                  value={getValues('customExamples')}
                  register={register}
                  type="array"
                  placeholder="Add your own examples"
                  isDirty={!!dirtyFields.customExamples}
                  isEditable={enableEditing}
                />

                <EditableField
                  label="Personal Notes"
                  name="customNotes"
                  value={getValues('customNotes')}
                  register={register}
                  type="textarea"
                  placeholder="Add personal notes about this word..."
                  maxLength={5000}
                  isDirty={!!dirtyFields.customNotes}
                  isEditable={enableEditing}
                />

                <EditableField
                  label="Custom Synonyms"
                  name="customSynonyms"
                  value={getValues('customSynonyms')}
                  register={register}
                  type="array"
                  placeholder="Add synonyms"
                  isDirty={!!dirtyFields.customSynonyms}
                  isEditable={enableEditing}
                />

                <EditableField
                  label="Custom Antonyms"
                  name="customAntonyms"
                  value={getValues('customAntonyms')}
                  register={register}
                  type="array"
                  placeholder="Add antonyms"
                  isDirty={!!dirtyFields.customAntonyms}
                  isEditable={enableEditing}
                />

                <EditableField
                  label="Tags"
                  name="customTags"
                  value={getValues('customTags')}
                  register={register}
                  type="array"
                  placeholder="Add tags (e.g., business, informal, advanced)"
                  isDirty={!!dirtyFields.customTags}
                  isEditable={enableEditing}
                />
              </div>
            </div>
          )}

          {/* Additional metadata */}
          <div className="border-t border-border pt-4 flex flex-wrap gap-4 text-sm">
            {wordData.difficulty && (
              <div>
                <span className="font-medium">Difficulty:</span>{' '}
                <span className="capitalize text-muted-foreground">{wordData.difficulty}</span>
              </div>
            )}
            {wordData.frequency !== undefined && (
              <div>
                <span className="font-medium">Frequency:</span>{' '}
                <span className="text-muted-foreground">{wordData.frequency}</span>
              </div>
            )}
            {wordData.styleTags && wordData.styleTags.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="font-medium">Tags:</span>
                <div className="flex gap-1">
                  {wordData.styleTags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-accent text-accent-foreground rounded-full text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Source URLs */}
          {wordData.sourceUrls && wordData.sourceUrls.length > 0 && (
            <div className="border-t border-border pt-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Sources</h3>
              <ul className="space-y-1">
                {wordData.sourceUrls.map((url, index) => (
                  <li key={index}>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline"
                    >
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
