import React, { useState, useMemo } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";

export interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowIdKey: keyof T;
  selectedRowId?: string | number | null;
  onRowClick?: (row: T) => void;
  zebra?: boolean;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  rowIdKey,
  selectedRowId,
  onRowClick,
  zebra = true,
  className = "",
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const handleHeaderClick = (column: Column<T>) => {
    if (!column.sortable) return;
    if (sortKey === column.key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortKey(column.key);
      setSortOrder("desc");
    }
  };

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    const sorted = [...data].sort((a, b) => {
      const aVal = a[sortKey as keyof T];
      const bVal = b[sortKey as keyof T];
      
      if (typeof aVal === "string" && typeof bVal === "string") {
        return aVal.localeCompare(bVal);
      }
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [data, sortKey, sortOrder]);

  return (
    <div className={`w-full overflow-x-auto custom-scrollbar ${className}`}>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-border shrink-0 bg-surface">
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => handleHeaderClick(col)}
                className={`px-3 py-2 text-section-title font-semibold text-[11px] leading-tight select-none ${
                  col.sortable ? "cursor-pointer hover:text-paper" : ""
                } ${col.className || ""}`}
              >
                <div className="flex items-center gap-1">
                  {col.label}
                  {col.sortable && sortKey === col.key && (
                    <span>
                      {sortOrder === "asc" ? (
                        <ChevronUp className="w-3 h-3 text-focus" />
                      ) : (
                        <ChevronDown className="w-3 h-3 text-focus" />
                      )}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate text-xs">
                Nenhum registro encontrado.
              </td>
            </tr>
          ) : (
            sortedData.map((row, idx) => {
              const isSelected = selectedRowId === (row[rowIdKey] as unknown as string | number | null);
              return (
                <tr
                  key={String(row[rowIdKey] || idx)}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`h-9 border-b border-border/30 transition-colors ${
                    onRowClick ? "cursor-pointer" : ""
                  } ${
                    isSelected
                      ? "bg-[var(--color-focus-bg)] text-paper"
                      : zebra && idx % 2 !== 0
                      ? "bg-[var(--color-surface-raised)]/45"
                      : "bg-transparent"
                  } ${onRowClick ? "hover:bg-[var(--color-focus-bg)]/60" : ""}`}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-3 py-1.5 text-data truncate text-xs ${
                        col.className || ""
                      }`}
                    >
                      {col.render ? col.render(row) : String(row[col.key as keyof T] || "")}
                    </td>
                  ))}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
