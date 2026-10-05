"use client";
import { useEffect, useState } from "react";

type CancelledClasses = Record<string, number[]>;
export const NO_CANCELLED_DAYS: number[] = [];

export const getClassCancellationKey = (slot: any) =>
  `${slot.code || slot.courseCode || slot.course || slot.name}|${slot.time}`;

export function useClassCancellations() {
  const [cancelledClasses, setCancelledClasses] = useState<CancelledClasses>({});

  useEffect(() => {
    const load = () => {
      try {
        setCancelledClasses(JSON.parse(localStorage.getItem("ratio_cancelled_classes") || "{}"));
      } catch {
        setCancelledClasses({});
      }
    };
    load();
    window.addEventListener("class_cancellations_updated", load);
    return () => window.removeEventListener("class_cancellations_updated", load);
  }, []);

  const saveCancelledDays = (slot: any, days: number[]) => {
    const next = { ...cancelledClasses };
    const key = getClassCancellationKey(slot);
    const selected = [...new Set(days.filter((day) => day >= 1 && day <= 5))].sort();
    if (selected.length) next[key] = selected;
    else delete next[key];
    localStorage.setItem("ratio_cancelled_classes", JSON.stringify(next));
    setCancelledClasses(next);
    window.dispatchEvent(new Event("class_cancellations_updated"));
  };

  return { cancelledClasses, saveCancelledDays };
}
