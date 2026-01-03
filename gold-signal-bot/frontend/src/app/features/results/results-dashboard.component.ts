import {
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  ViewChild,
} from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatTabsModule } from "@angular/material/tabs";
import { MatTableModule } from "@angular/material/table";
import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { BaseChartDirective } from "ng2-charts";
import { ChartConfiguration } from "chart.js";
import { BacktestResults, Trade } from "../../core/models/models";

@Component({
  selector: "app-results-dashboard",
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTabsModule,
    MatTableModule,
    MatIconModule,
    MatButtonModule,
    BaseChartDirective,
  ],
  templateUrl: "./results-dashboard.component.html",
  styleUrls: ["./results-dashboard.component.scss"],
})
export class ResultsDashboardComponent implements OnChanges {
  @Input() results: BacktestResults | null = null;
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  displayedColumns: string[] = [
    "timestamp",
    "type",
    "entry_price",
    "sl",
    "tp",
    "close_price",
    "pips",
    "confidence",
  ];

  // Chart data
  equityChartData: ChartConfiguration["data"] = {
    datasets: [],
  };

  equityChartOptions: ChartConfiguration["options"] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
        labels: { color: "rgba(255, 255, 255, 0.7)" },
      },
      title: {
        display: true,
        text: "Equity Growth (%)",
        color: "rgba(255, 255, 255, 0.9)",
        font: { size: 16, weight: "bold" },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const val = context.parsed.y;
            return `Return: ${val !== null ? val.toLocaleString() : "0"}%`;
          },
        },
      },
    },
    scales: {
      x: {
        type: "time",
        time: { unit: "day" },
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: { color: "rgba(255, 255, 255, 0.5)" },
      },
      y: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: {
          color: "rgba(255, 255, 255, 0.5)",
          callback: (val) => val + "%",
        },
      },
    },
  };

  monthlyChartData: ChartConfiguration["data"] = {
    datasets: [],
  };

  monthlyChartOptions: ChartConfiguration["options"] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: "Monthly Performance (%)",
        color: "rgba(255, 255, 255, 0.9)",
        font: { size: 16, weight: "bold" },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const val = context.parsed.y;
            return `Return: ${val !== null ? val : "0"}%`;
          },
        },
      },
    },
    scales: {
      y: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: {
          color: "rgba(255, 255, 255, 0.5)",
          callback: (val) => val + "%",
        },
      },
      x: {
        grid: { display: false },
        ticks: { color: "rgba(255, 255, 255, 0.5)" },
      },
    },
  };

  ngOnChanges(changes: SimpleChanges) {
    if (changes["results"] && this.results) {
      this.updateChartData();
    }
  }

  updateChartData() {
    if (!this.results) return;

    // Equity Percentage Chart
    const initialBalance = this.results.metrics.initial_balance || 10000;
    const labels = this.results.equity_curve.map((point) =>
      point.timestamp === "Start"
        ? new Date(this.results!.trades[0]?.timestamp || Date.now())
        : new Date(point.timestamp)
    );
    const data = this.results.equity_curve.map((point) => {
      const balance = point.balance || initialBalance;
      const percentGain = ((balance - initialBalance) / initialBalance) * 100;
      return Number(percentGain.toFixed(2));
    });

    this.equityChartData = {
      labels,
      datasets: [
        {
          label: "Equity Growth (%)",
          data,
          borderColor: "#9262f9",
          backgroundColor: "rgba(146, 98, 249, 0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: labels.length > 50 ? 0 : 3,
        },
      ],
    };

    // Monthly Performance Chart
    if (this.results.monthly_performance) {
      this.monthlyChartData = {
        labels: this.results.monthly_performance.map((m) => m.month),
        datasets: [
          {
            label: "Monthly %",
            data: this.results.monthly_performance.map((m) => m.percent),
            backgroundColor: this.results.monthly_performance.map((m) =>
              m.percent >= 0
                ? "rgba(76, 175, 80, 0.6)"
                : "rgba(244, 67, 54, 0.6)"
            ),
            borderColor: this.results.monthly_performance.map((m) =>
              m.percent >= 0 ? "#4caf50" : "#f44336"
            ),
            borderWidth: 1,
          },
        ],
      };
    }

    this.chart?.update();
  }

  copyReport() {
    if (!this.results) return;

    const m = this.results.metrics;
    const netReturn = this.getNetReturn();
    const report = `📊 TRADE SUMMARY:
   Total Signals: ${m.total_trades}
   Closed Trades: ${m.closed_trades}
   Open Trades: ${m.open_trades}

💰 P&L METRICS (Total):
   Total Profit: $${
     m.total_profit_money?.toLocaleString() || "0"
   } (${netReturn}%)
   Total Pips: ${m.total_pips}
   Winning Trades: ${m.winning_trades} ✅
   Losing Trades: ${m.losing_trades} ❌
   Win Rate: ${m.win_rate}%
   Avg Win: $${m.avg_win_money?.toLocaleString() || "0"} (${m.avg_win} pips)
   Avg Loss: $${m.avg_loss_money?.toLocaleString() || "0"} (${m.avg_loss} pips)
   Profit Factor: ${m.profit_factor}`;

    navigator.clipboard.writeText(report).then(() => {
      // You could add a toast notification here if available
      alert("Report copied to clipboard!");
    });
  }

  exportToCSV() {
    if (!this.results) return;

    const csvContent = this.generateCSV();
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `backtest_results_${new Date().toISOString()}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  private generateCSV(): string {
    if (!this.results) return "";

    const headers = [
      "Timestamp",
      "Type",
      "Entry Price",
      "SL",
      "TP",
      "Close Price",
      "Close Timestamp",
      "Pips",
      "Confidence",
    ];
    const rows = this.results.trades.map((trade) => [
      trade.timestamp,
      trade.type,
      trade.entry_price,
      trade.sl,
      trade.tp,
      trade.close_price || "",
      trade.close_timestamp || "",
      trade.pips || "",
      trade.confidence,
    ]);

    return [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");
  }

  getTradeClass(trade: Trade): string {
    if (!trade.pips) return "";
    return trade.pips > 0 ? "positive" : "negative";
  }

  getNetReturn(): string {
    if (!this.results || !this.results.metrics.initial_balance) return "0.00";
    const initial = this.results.metrics.initial_balance;
    const final = this.results.metrics.final_balance || initial;
    const netReturn = ((final - initial) / initial) * 100;
    return netReturn.toFixed(2);
  }
}
