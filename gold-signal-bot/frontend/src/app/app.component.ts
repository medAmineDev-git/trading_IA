import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [RouterOutlet, MatToolbarModule, MatIconModule],
  template: `
    <nav class="navbar">
      <div class="container nav-content">
        <div class="logo">
          <mat-icon class="icon">show_chart</mat-icon>
          <span class="text-gradient">FundedLab</span>
        </div>
        <div class="nav-links">
          <!-- Placeholder links for now -->
        </div>
        <button class="btn-primary">Connect Wallet</button>
      </div>
    </nav>
    <div class="app-container">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [
    `
      .logo {
        display: flex;
        align-items: center;
        gap: 8px;

        .icon {
          color: var(--text-accent);
        }
      }

      .app-container {
        min-height: calc(100vh - 80px); /* Adjust for navbar height */
      }
    `,
  ],
})
export class AppComponent {
  title = "Gold Signal Bot Dashboard";
}
