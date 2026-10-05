"use client";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { getClassCancellationKey } from "@/hooks/useClassCancellations";

interface ClassCancellationDialogProps {
  slot: any;
  cancelledDays: number[];
  onClose: () => void;
  onSave: (days: number[]) => void;
}

export default function ClassCancellationDialog({
  slot,
  cancelledDays,
  onClose,
  onSave,
}: ClassCancellationDialogProps) {
  const [selectedDays, setSelectedDays] = useState<number[]>(cancelledDays);
  const slotKey = slot ? getClassCancellationKey(slot) : null;

  useEffect(() => setSelectedDays(cancelledDays), [slotKey, cancelledDays]);

  if (!slot) return null;

  const toggleDay = (day: number) => {
    setSelectedDays((selected) =>
      selected.includes(day)
        ? selected.filter((item) => item !== day)
        : [...selected, day].sort(),
    );
  };

  return (
    <div
      className="fixed inset-0 z-[80] flex items-end sm:items-center justify-center bg-black/50 p-4"
      onMouseDown={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="class-cancellation-title"
        className="w-full max-w-sm rounded-3xl bg-theme-bg border border-theme-border p-6 shadow-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 mb-2">
          <div>
            <h2 id="class-cancellation-title" className="text-lg font-black uppercase tracking-wide text-theme-text">
              Class cancellation
            </h2>
            <p className="mt-1 text-sm text-theme-muted">
              {slot.name || slot.courseTitle || slot.course || slot.code} · {slot.time}
            </p>
          </div>
          <button type="button" aria-label="Close" onClick={onClose} className="p-2 rounded-full text-theme-muted hover:bg-theme-surface">
            <X size={18} />
          </button>
        </div>
        <p className="text-xs text-theme-muted mb-4">Choose the day orders when this class is cancelled.</p>
        <div className="grid grid-cols-5 gap-2 mb-6">
          {[1, 2, 3, 4, 5].map((day) => (
            <button
              key={day}
              type="button"
              aria-pressed={selectedDays.includes(day)}
              onClick={() => toggleDay(day)}
              className={`rounded-xl border px-2 py-3 text-xs font-bold transition-colors ${selectedDays.includes(day) ? "bg-theme-emphasis text-theme-bg border-theme-emphasis" : "bg-theme-surface text-theme-muted border-theme-border"}`}
            >
              Day {day}
            </button>
          ))}
        </div>
        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="flex-1 rounded-xl border border-theme-border py-3 text-sm font-bold text-theme-muted">
            Close
          </button>
          <button type="button" onClick={() => onSave(selectedDays)} className="flex-1 rounded-xl bg-theme-emphasis py-3 text-sm font-bold text-theme-bg">
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
