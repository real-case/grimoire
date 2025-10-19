'use client'

/**
 * Editable Field Component
 *
 * Provides inline editing functionality with visual distinction for edited fields.
 * Integrates with React Hook Form for form state management.
 *
 * Features:
 * - Inline editing (click to edit, FR-004)
 * - Visual distinction for edited fields (FR-010)
 * - Support for text, textarea, and array inputs
 * - Empty field values allowed (per clarification)
 */

import { useState } from 'react'
import type { UseFormRegister, FieldValues, Path } from 'react-hook-form'

export interface EditableFieldProps<T extends FieldValues> {
  label: string
  name: Path<T>
  value: string | string[] | null | undefined
  register: UseFormRegister<T>
  type?: 'text' | 'textarea' | 'array'
  placeholder?: string
  maxLength?: number
  isDirty?: boolean
  isEditable?: boolean
  className?: string
}

export default function EditableField<T extends FieldValues>({
  label,
  name,
  value,
  register,
  type = 'text',
  placeholder = 'Click to edit...',
  maxLength,
  isDirty = false,
  isEditable = true,
  className = '',
}: EditableFieldProps<T>) {
  const [isEditing, setIsEditing] = useState(false)
  const displayValue = Array.isArray(value) ? value.join(', ') : value || ''

  const handleClick = () => {
    if (isEditable) {
      setIsEditing(true)
    }
  }

  const handleBlur = () => {
    setIsEditing(false)
  }

  // Common input classes
  const baseInputClass =
    'w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
  const editedClass = isDirty ? 'bg-accent/20 border-primary' : ''

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label with edited indicator */}
      <div className="flex items-center gap-2">
        <label className="block text-sm font-medium text-foreground">
          {label}
        </label>
        {isDirty && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary">
            Edited
          </span>
        )}
      </div>

      {/* Editable content */}
      {isEditable ? (
        <>
          {isEditing ? (
            // Edit mode
            <>
              {type === 'textarea' ? (
                <textarea
                  {...register(name)}
                  className={`${baseInputClass} ${editedClass} min-h-[100px] resize-y`}
                  placeholder={placeholder}
                  maxLength={maxLength}
                  autoFocus
                  onBlur={handleBlur}
                />
              ) : type === 'array' ? (
                <input
                  {...register(name)}
                  type="text"
                  className={`${baseInputClass} ${editedClass}`}
                  placeholder={`${placeholder} (comma-separated)`}
                  maxLength={maxLength}
                  autoFocus
                  onBlur={handleBlur}
                />
              ) : (
                <input
                  {...register(name)}
                  type="text"
                  className={`${baseInputClass} ${editedClass}`}
                  placeholder={placeholder}
                  maxLength={maxLength}
                  autoFocus
                  onBlur={handleBlur}
                />
              )}
            </>
          ) : (
            // Display mode (click to edit)
            <div
              onClick={handleClick}
              className={`w-full px-3 py-2 border rounded-md cursor-pointer hover:bg-muted/50 transition-colors ${
                editedClass || 'border-border'
              } ${!displayValue ? 'text-muted-foreground italic' : 'text-foreground'}`}
            >
              {displayValue || placeholder}
            </div>
          )}
        </>
      ) : (
        // Read-only display
        <div className="w-full px-3 py-2 border border-border rounded-md bg-muted/30 text-muted-foreground">
          {displayValue || 'Not available'}
        </div>
      )}

      {/* Character count for long text fields */}
      {isEditing && maxLength && type !== 'array' && (
        <p className="text-xs text-muted-foreground text-right">
          {displayValue.length} / {maxLength}
        </p>
      )}
    </div>
  )
}