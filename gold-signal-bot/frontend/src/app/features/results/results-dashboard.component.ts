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
      },
      title: {
        display: true,
        text: "Equity Curve (Cumulative Pips)",
      },
    },
    scales: {
      x: {
        type: "time",
        time: {
          unit: "day",
        },
        title: {
          display: true,
          text: "Date",
        },
      },
      y: {
        title: {
          display: true,
          text: "Cumulative Pips",
        },
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

    const labels = this.results.equity_curve.map(
      (point) => new Date(point.timestamp)
    );
    const data = this.results.equity_curve.map((point) => point.pips);

    this.equityChartData = {
      labels,
      datasets: [
        {
          label: "Cumulative Pips",
          data,
          borderColor: "#3f51b5",
          backgroundColor: "rgba(63, 81, 181, 0.1)",
          fill: true,
          tension: 0.4,
        },
      ],
    };

    this.chart?.update();
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
}
