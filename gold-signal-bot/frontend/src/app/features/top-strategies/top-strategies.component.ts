import { Component, EventEmitter, OnInit, Output } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatTableModule } from "@angular/material/table";
import { MatIconModule } from "@angular/material/icon";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import { MatButtonModule } from "@angular/material/button";
import { ApiService } from "../../core/services/api.service";
import { Strategy } from "../../core/models/models";

@Component({
  selector: "app-top-strategies",
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatSlideToggleModule,
    MatButtonModule,
  ],
  templateUrl: "./top-strategies.component.html",
  styleUrls: ["./top-strategies.component.scss"],
})
export class TopStrategiesComponent implements OnInit {
  @Output() backtestSelected = new EventEmitter<Strategy>();
  strategies: any[] = []; // Changed to any[] to allow for client-side additions like connectedClients
  loading = true;
  displayedColumns: string[] = [
    "name",
    "gainPercent",
    "winRate",
    "profitFactor",
    "trades",
    "age",
    "connectedClients",
    "backtest",
    "actions",
  ];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadStrategies();
  }

  loadStrategies(): void {
    this.loading = true;
    this.apiService.getStrategies().subscribe({
      next: (data) => {
        // Calculate gain percent and sort
        const processedData = data.map((s: any) => {
          const initial = s.backtest.metrics.initial_balance || 10000;
          const final = s.backtest.metrics.final_balance || initial;
          const gain_percent = ((final - initial) / initial) * 100;
          return { ...s, gain_percent };
        });

        const sortedData = processedData.sort((a: any, b: any) => {
          // 1. Gain Percent (DESC)
          if (b.gain_percent !== a.gain_percent)
            return b.gain_percent - a.gain_percent;

          // 2. Win Rate (DESC)
          const winRateA = a.backtest.metrics.win_rate;
          const winRateB = b.backtest.metrics.win_rate;
          if (winRateB !== winRateA) return winRateB - winRateA;

          // 3. Profit Factor (DESC)
          const pfA = a.backtest.metrics.profit_factor;
          const pfB = b.backtest.metrics.profit_factor;
          return pfB - pfA;
        });

        // Add random connected clients
        this.strategies = sortedData.map((s) => ({
          ...s,
          connectedClients: Math.floor(Math.random() * 401) + 100, // 100 to 500
        }));

        this.loading = false;
      },
      error: (err) => {
        console.error("Failed to load strategies:", err);
        this.loading = false;
      },
    });
  }

  toggleLive(strategy: any): void {
    const strategyId = strategy.id || strategy.backtest.timestamp;
    this.apiService.toggleStrategyLive(strategyId).subscribe({
      next: (res) => {
        strategy.is_live = res.is_live;
      },
    });
  }

  onBacktest(strategy: Strategy): void {
    this.backtestSelected.emit(strategy);
  }

  joinTelegram(strategy: any): void {
    const strategyId = strategy.id || strategy.backtest.timestamp;
    this.apiService.getTelegramLink(strategyId).subscribe({
      next: (res) => {
        window.open(res.link, "_blank");
      },
    });
  }

  getModelClass(type: string | undefined): string {
    return (type || "xgboost").toLowerCase();
  }

  isTopPerformer(strategy: Strategy): boolean {
    if (this.strategies.length < 2) return false;
    const maxWinRate = Math.max(
      ...this.strategies.map((s) => s.backtest.metrics.win_rate)
    );
    return strategy.backtest.metrics.win_rate === maxWinRate && maxWinRate > 0;
  }
}
