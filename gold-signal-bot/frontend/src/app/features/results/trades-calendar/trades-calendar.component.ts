import { Component, Input, OnChanges, SimpleChanges } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatCardModule } from "@angular/material/card";
import { MatTooltipModule } from "@angular/material/tooltip";
import {
  BacktestResults,
  Trade,
  EquityPoint,
} from "../../../core/models/models";

interface DayData {
  date: Date;
  dayOfMonth: number;
  returnPercent: number;
  tradeCount: number;
  hasTrade: boolean;
  isPadding: boolean; // For empty cells from prev/next entries
}

@Component({
  selector: "app-trades-calendar",
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTooltipModule,
  ],
  templateUrl: "./trades-calendar.component.html",
  styleUrls: ["./trades-calendar.component.scss"],
})
export class TradesCalendarComponent implements OnChanges {
  @Input() results: BacktestResults | null = null;

  currentViewDate: Date = new Date(); // Defaults to now, but updates to data start
  calendarDays: DayData[] = [];
  weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  // Cache for daily data
  private dailyStats = new Map<string, { percent: number; count: number }>();

  ngOnChanges(changes: SimpleChanges) {
    if (changes["results"] && this.results) {
      this.processData();

      // Set initial view to the last month of data
      if (this.results?.equity_curve && this.results.equity_curve.length > 0) {
        const lastPoint =
          this.results.equity_curve[this.results.equity_curve.length - 1];
        if (lastPoint.timestamp !== "Start") {
          this.currentViewDate = new Date(lastPoint.timestamp);
        }
      }

      this.generateCalendar();
    }
  }

  private processData() {
    this.dailyStats.clear();
    if (!this.results || !this.results.daily_performance) return;

    // Use backend-calculated daily performance for 100% accuracy
    Object.entries(this.results.daily_performance).forEach(
      ([dateStr, data]) => {
        // dateStr is already YYYY-MM-DD from backend
        this.dailyStats.set(dateStr, {
          percent: data.percent,
          count: data.count,
        });
      }
    );
  }

  // Helper to get YYYY-MM-DD from Date object
  private formatDateKey(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  generateCalendar() {
    const year = this.currentViewDate.getFullYear();
    const month = this.currentViewDate.getMonth();

    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);

    const startDayOfWeek = firstDayOfMonth.getDay(); // 0 (Sun) to 6 (Sat)
    const daysInMonth = lastDayOfMonth.getDate();

    this.calendarDays = [];

    // Add padding for previous month
    for (let i = 0; i < startDayOfWeek; i++) {
      this.calendarDays.push({
        date: new Date(year, month, 0 - (startDayOfWeek - 1 - i)), // Mock date
        dayOfMonth: 0,
        returnPercent: 0,
        tradeCount: 0,
        hasTrade: false,
        isPadding: true,
      });
    }

    // Add actual days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateKey = this.formatDateKey(date);
      const stats = this.dailyStats.get(dateKey);

      this.calendarDays.push({
        date: date,
        dayOfMonth: day,
        returnPercent: stats ? stats.percent : 0,
        tradeCount: stats ? stats.count : 0,
        hasTrade: !!stats, // Only true if we actually have a record
        isPadding: false,
      });
    }
  }

  selectedDay: DayData | null = null;
  selectedTrades: Trade[] = [];

  selectDay(day: DayData) {
    if (day.isPadding) return;

    this.selectedDay = day;

    // Filter trades for this day
    if (this.results) {
      const dayDateKey = this.formatDateKey(day.date);
      this.selectedTrades = (this.results.trades || []).filter((trade) => {
        // Use close_timestamp if available, else timestamp
        const tradeDateStr = trade.close_timestamp || trade.timestamp;
        const tradeDate = new Date(tradeDateStr);
        return this.formatDateKey(tradeDate) === dayDateKey;
      });
    } else {
      this.selectedTrades = [];
    }
  }

  prevMonth() {
    this.currentViewDate = new Date(
      this.currentViewDate.getFullYear(),
      this.currentViewDate.getMonth() - 1,
      1
    );
    this.generateCalendar();
  }

  nextMonth() {
    this.currentViewDate = new Date(
      this.currentViewDate.getFullYear(),
      this.currentViewDate.getMonth() + 1,
      1
    );
    this.generateCalendar();
  }

  getDayClass(day: DayData): string {
    if (day.isPadding) return "padding-day";

    // Logic:
    // If trade count > 0 OR return != 0 => It's an active day
    // Color based on Return %
    if (day.hasTrade || day.returnPercent !== 0) {
      if (day.returnPercent > 0) return "positive-day";
      if (day.returnPercent < 0) return "negative-day";
      return "neutral-day"; // Break even
    }

    return "empty-day";
  }
}
