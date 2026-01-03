import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { MatTableModule } from "@angular/material/table";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatSnackBar } from "@angular/material/snack-bar";
import { ApiService } from "../../core/services/api.service";
import { Strategy } from "../../core/models/models";

@Component({
  selector: "app-my-strategies",
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
  ],
  template: `
    <div class="strategies-container">
      <div class="header">
        <h2>My Strategies</h2>
        <button mat-raised-button color="primary" (click)="loadStrategies()">
          <mat-icon>refresh</mat-icon> Refresh
        </button>
      </div>

      <div class="table-container glass-panel">
        <table mat-table [dataSource]="strategies" class="mat-elevation-z8">
          <!-- Name Column -->
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef>Strategy Name</th>
            <td mat-cell *matCellDef="let strategy" class="name-cell">
              {{ strategy.name }}
              <span class="publish-badge" *ngIf="strategy.is_published">
                PUBLISHED
              </span>
            </td>
          </ng-container>

          <!-- Gain Column -->
          <ng-container matColumnDef="gain">
            <th mat-header-cell *matHeaderCellDef>Gain (%)</th>
            <td
              mat-cell
              *matCellDef="let strategy"
              [class.positive]="
                strategy.backtest.metrics.total_profit_money > 0
              "
              [class.negative]="
                strategy.backtest.metrics.total_profit_money < 0
              "
            >
              {{
                (strategy.backtest.metrics.total_profit_money / 10000) * 100
                  | number : "1.2-2"
              }}%
            </td>
          </ng-container>

          <!-- Win Rate Column -->
          <ng-container matColumnDef="winRate">
            <th mat-header-cell *matHeaderCellDef>Win Rate</th>
            <td mat-cell *matCellDef="let strategy">
              {{ strategy.backtest.metrics.win_rate * 100 | number : "1.1-1" }}%
            </td>
          </ng-container>

          <!-- Profit Factor Column -->
          <ng-container matColumnDef="profitFactor">
            <th mat-header-cell *matHeaderCellDef>PF</th>
            <td mat-cell *matCellDef="let strategy">
              {{ strategy.backtest.metrics.profit_factor | number : "1.2-2" }}
            </td>
          </ng-container>

          <!-- Trades Column -->
          <ng-container matColumnDef="trades">
            <th mat-header-cell *matHeaderCellDef>Trades</th>
            <td mat-cell *matCellDef="let strategy">
              {{ strategy.backtest.metrics.total_trades }}
            </td>
          </ng-container>

          <!-- Age (Days) Column -->
          <ng-container matColumnDef="age">
            <th mat-header-cell *matHeaderCellDef>Age (Days)</th>
            <td mat-cell *matCellDef="let strategy">
              {{ strategy.backtest.metrics.period_days || "N/A" }}
            </td>
          </ng-container>

          <!-- Actions Column -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef>Actions</th>
            <td mat-cell *matCellDef="let strategy">
              <button
                mat-icon-button
                [color]="strategy.is_published ? 'accent' : ''"
                (click)="togglePublish(strategy)"
                [matTooltip]="
                  strategy.is_published
                    ? 'Unpublish strategy'
                    : 'Publish to Top Strategies'
                "
              >
                <mat-icon>{{
                  strategy.is_published ? "public" : "public_off"
                }}</mat-icon>
              </button>
              <button
                mat-icon-button
                color="warn"
                (click)="deleteStrategy(strategy)"
                matTooltip="Delete Strategy"
              >
                <mat-icon>delete</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns"></tr>

          <tr class="mat-row" *matNoDataRow>
            <td
              class="mat-cell"
              colspan="7"
              style="text-align: center; padding: 20px;"
            >
              No strategies found. Save a backtest result to see it here.
            </td>
          </tr>
        </table>
      </div>
    </div>
  `,
  styles: [
    `
      .strategies-container {
        padding: 24px;
      }

      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
      }

      .header h2 {
        margin: 0;
        font-size: 1.5rem;
        color: var(--text-primary);
      }

      .table-container {
        overflow: hidden;
        border-radius: 8px;
      }

      table {
        width: 100%;
      }

      .name-cell {
        font-weight: 500;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .publish-badge {
        font-size: 0.7rem;
        background: rgba(76, 175, 80, 0.1);
        color: #4caf50;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(76, 175, 80, 0.3);
      }

      .positive {
        color: #4caf50;
        font-weight: 500;
      }

      .negative {
        color: #f44336;
        font-weight: 500;
      }
    `,
  ],
})
export class MyStrategiesComponent implements OnInit {
  strategies: Strategy[] = [];
  displayedColumns: string[] = [
    "name",
    "gain",
    "winRate",
    "profitFactor",
    "trades",
    "age",
    "actions",
  ];

  constructor(private apiService: ApiService, private snackBar: MatSnackBar) {}

  ngOnInit() {
    this.loadStrategies();
  }

  loadStrategies() {
    this.apiService.getMyStrategies().subscribe({
      next: (data) => {
        this.strategies = data;
      },
      error: (error) => {
        console.error("Error loading strategies", error);
        this.snackBar.open("Failed to load strategies", "Close", {
          duration: 3000,
        });
      },
    });
  }

  togglePublish(strategy: Strategy) {
    this.apiService.publishStrategy(strategy.id).subscribe({
      next: (response) => {
        strategy.is_published = response.is_published;
        this.snackBar.open(
          strategy.is_published
            ? "Strategy Published!"
            : "Strategy Unpublished",
          "Close",
          { duration: 2000 }
        );
      },
      error: (error) => {
        this.snackBar.open("Failed to update status", "Close", {
          duration: 3000,
        });
      },
    });
  }

  deleteStrategy(strategy: Strategy) {
    if (!confirm(`Are you sure you want to delete "${strategy.name}"?`)) return;

    this.apiService.removeStrategy(strategy.id).subscribe({
      next: () => {
        this.strategies = this.strategies.filter((s) => s.id !== strategy.id);
        this.snackBar.open("Strategy deleted", "Close", { duration: 2000 });
      },
      error: (error) => {
        this.snackBar.open("Failed to delete strategy", "Close", {
          duration: 3000,
        });
      },
    });
  }
}
