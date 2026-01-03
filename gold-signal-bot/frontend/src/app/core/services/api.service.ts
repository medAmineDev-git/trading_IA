import { Injectable } from "@angular/core";
import { HttpClient, HttpErrorResponse } from "@angular/common/http";
import { Observable, throwError, interval } from "rxjs";
import { catchError, switchMap, takeWhile } from "rxjs/operators";
import {
  Config,
  DataFile,
  TrainingParams,
  BacktestParams,
  JobStatus,
  TrainingResults,
  BacktestResults,
  Strategy,
} from "../models/models";

@Injectable({
  providedIn: "root",
})
export class ApiService {
  private baseUrl = "http://127.0.0.1:5000/api";

  constructor(private http: HttpClient) {}

  // Configuration endpoints
  getConfig(): Observable<Config> {
    return this.http
      .get<Config>(`${this.baseUrl}/config`)
      .pipe(catchError(this.handleError));
  }

  getDataFiles(): Observable<{ files: DataFile[] }> {
    return this.http
      .get<{ files: DataFile[] }>(`${this.baseUrl}/data-files`)
      .pipe(catchError(this.handleError));
  }

  // Training endpoints
  startTraining(
    params: TrainingParams
  ): Observable<{ job_id: string; status: string }> {
    return this.http
      .post<{ job_id: string; status: string }>(`${this.baseUrl}/train`, params)
      .pipe(catchError(this.handleError));
  }

  getTrainingStatus(jobId: string): Observable<JobStatus> {
    return this.http
      .get<JobStatus>(`${this.baseUrl}/train/status/${jobId}`)
      .pipe(catchError(this.handleError));
  }

  getTrainingResults(jobId: string): Observable<TrainingResults> {
    return this.http
      .get<TrainingResults>(`${this.baseUrl}/train/results/${jobId}`)
      .pipe(catchError(this.handleError));
  }

  // Poll training status until complete
  pollTrainingStatus(jobId: string): Observable<JobStatus> {
    return interval(1000).pipe(
      switchMap(() => this.getTrainingStatus(jobId)),
      takeWhile(
        (status) => status.status === "pending" || status.status === "running",
        true
      )
    );
  }

  // Backtest endpoints
  startBacktest(
    params: BacktestParams
  ): Observable<{ job_id: string; status: string }> {
    return this.http
      .post<{ job_id: string; status: string }>(
        `${this.baseUrl}/backtest`,
        params
      )
      .pipe(catchError(this.handleError));
  }

  getBacktestStatus(jobId: string): Observable<JobStatus> {
    return this.http
      .get<JobStatus>(`${this.baseUrl}/backtest/status/${jobId}`)
      .pipe(catchError(this.handleError));
  }

  getBacktestResults(jobId: string): Observable<BacktestResults> {
    return this.http
      .get<BacktestResults>(`${this.baseUrl}/backtest/results/${jobId}`)
      .pipe(catchError(this.handleError));
  }

  // Poll backtest status until complete
  pollBacktestStatus(jobId: string): Observable<JobStatus> {
    return interval(1000).pipe(
      switchMap(() => this.getBacktestStatus(jobId)),
      takeWhile(
        (status) => status.status === "pending" || status.status === "running",
        true
      )
    );
  }

  toggleStrategyLive(strategyId: string): Observable<any> {
    return this.http
      .post<any>(`${this.baseUrl}/strategies/${strategyId}/toggle-live`, {})
      .pipe(catchError(this.handleError));
  }

  getTelegramLink(strategyId: string): Observable<{ link: string }> {
    return this.http
      .get<{ link: string }>(
        `${this.baseUrl}/strategies/telegram-link/${strategyId}`
      )
      .pipe(catchError(this.handleError));
  }

  getStrategies(): Observable<Strategy[]> {
    return this.http
      .get<Strategy[]>(`${this.baseUrl}/strategies`)
      .pipe(catchError(this.handleError));
  }

  // Auth endpoints
  register(data: any): Observable<any> {
    return this.http
      .post(`${this.baseUrl}/auth/register`, data)
      .pipe(catchError(this.handleError));
  }

  login(data: any): Observable<any> {
    return this.http
      .post(`${this.baseUrl}/auth/login`, data)
      .pipe(catchError(this.handleError));
  }

  // Personal Strategy Management
  getMyStrategies(): Observable<Strategy[]> {
    return this.http
      .get<Strategy[]>(`${this.baseUrl}/my-strategies`)
      .pipe(catchError(this.handleError));
  }

  savePersonalStrategy(name: string): Observable<any> {
    return this.http
      .post(`${this.baseUrl}/strategies/save`, { name })
      .pipe(catchError(this.handleError));
  }

  publishStrategy(strategyId: string): Observable<any> {
    return this.http
      .post(`${this.baseUrl}/strategies/publish`, { strategy_id: strategyId })
      .pipe(catchError(this.handleError));
  }

  removeStrategy(strategyId: string): Observable<any> {
    return this.http
      .delete(`${this.baseUrl}/strategies/remove`, {
        params: { strategy_id: strategyId },
      })
      .pipe(catchError(this.handleError));
  }

  // Health check
  healthCheck(): Observable<{ status: string; timestamp: string }> {
    return this.http
      .get<{ status: string; timestamp: string }>(`${this.baseUrl}/health`)
      .pipe(catchError(this.handleError));
  }

  // Error handling
  private handleError(error: HttpErrorResponse) {
    let errorMessage = "An unknown error occurred";

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Server Error: ${error.status}\nMessage: ${error.message}`;
      if (error.error?.error) {
        errorMessage = error.error.error;
      }
    }

    console.error("API Error:", errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
