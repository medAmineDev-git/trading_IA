import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [RouterOutlet, MatToolbarModule, MatIconModule],
  template: `
    <header class="main-header">
      <!-- Line 1: Logo, Search, Auth -->
      <div class="header-line-1">
        <div class="container line-1-content">
          <div class="logo">
            <mat-icon class="icon">show_chart</mat-icon>
            <span class="text-gradient">FundedLab</span>
          </div>

          <div class="search-container">
            <div class="search-bar">
              <mat-icon class="search-icon">search</mat-icon>
              <input
                type="text"
                placeholder="Search strategies, indicators..."
              />
            </div>
          </div>

          <div class="nav-actions">
            <button class="btn-login">Log in</button>
            <button class="btn-primary">Sign Up</button>
          </div>
        </div>
      </div>

      <!-- Line 2: Navigation Links -->
      <div class="header-line-2">
        <div class="container line-2-content">
          <div class="nav-links">
            <a href="#" class="nav-link active">Home</a>
            <a href="#" class="nav-link">Strategy Planner IA</a>
            <a href="#" class="nav-link">TradingView Indicators</a>
            <a href="#" class="nav-link">Forex Copy Trading</a>
            <a href="#" class="nav-link">Signal Alerts</a>
          </div>
        </div>
      </div>
    </header>

    <div class="app-container">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [
    `
      .main-header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: var(--bg-primary);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      }

      .header-line-1 {
        height: 70px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      }

      .line-1-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
      }

      .logo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 1.5rem;
        cursor: pointer;
        min-width: 150px;

        .icon {
          color: var(--text-accent);
          font-size: 28px;
          height: 28px;
          width: 28px;
        }
      }

      .search-container {
        flex: 1;
        max-width: 600px;
      }

      .search-bar {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 50px;
        height: 40px;
        display: flex;
        align-items: center;
        padding: 0 16px;
        gap: 12px;
        transition: border-color 0.2s, background 0.2s;

        &:focus-within {
          border-color: var(--text-accent);
          background: rgba(255, 255, 255, 0.08);
        }

        .search-icon {
          color: var(--text-secondary);
          font-size: 20px;
          width: 20px;
          height: 20px;
        }

        input {
          background: transparent;
          border: none;
          color: white;
          width: 100%;
          outline: none;
          font-size: 14px;
          font-family: var(--font-body);

          &::placeholder {
            color: var(--text-muted);
          }
        }
      }

      .nav-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 220px;
        justify-content: flex-end;
      }

      .btn-login {
        background: transparent;
        border: none;
        color: var(--text-primary);
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        padding: 8px 16px;
        border-radius: 50px;
        transition: background 0.2s;

        &:hover {
          background: rgba(255, 255, 255, 0.05);
        }
      }

      .header-line-2 {
        height: 50px;
        display: flex;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.02);
      }

      .line-2-content {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
      }

      .nav-links {
        display: flex;
        align-items: center;
        gap: 24px;
      }

      .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0.2px;
        transition: color 0.2s, border-color 0.2s;
        padding: 14px 0;
        border-bottom: 2px solid transparent;
        white-space: nowrap;

        &:hover {
          color: var(--text-primary);
        }

        &.active {
          color: var(--text-primary);
          border-bottom-color: var(--text-accent);
        }
      }

      .app-container {
        min-height: calc(100vh - 120px);
        background-color: var(--bg-primary);
      }
    `,
  ],
})
export class AppComponent {
  title = "Gold Signal Bot Dashboard";
}
