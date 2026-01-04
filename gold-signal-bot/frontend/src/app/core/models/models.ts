export interface TrainingParams {
  indicators: {
    rsi_period: number;
    macd_fast: number;
    macd_slow: number;
    macd_signal: number;
    bb_period: number;
    bb_std_dev: number;
    atr_period: number;
    ema_fast: number;
    ema_slow: number;
  };
  risk: {
    stop_loss_percent: number;
    take_profit_percent: number;
    prob_threshold: number;
    use_atr_stops: boolean;
    use_trend_filter: boolean;
    use_volatility_filter: boolean;
    atr_filter_min: number;
    atr_filter_max: number;
  };
  model: {
    model_type: "xgboost" | "lightgbm" | "rf" | "ensemble";
    n_estimators: number;
    max_depth: number;
    min_samples_split: number;
  };
  data: {
    csv_path?: string;
    training_period?: string;
  };
}

export interface BacktestParams {
  period_days: number;
  initial_capital?: number;
}

export interface JobStatus {
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  message: string;
  updated_at: string;
}

export interface TrainingResults {
  metadata: {
    [key: string]: string;
  };
  output: string;
  model_path: string;
  timestamp: string;
}

export interface Trade {
  timestamp: string;
  type: "BUY" | "SELL";
  entry_price: number;
  sl: number;
  tp: number;
  close_price: number | null;
  close_timestamp: string | null;
  close_reason: string | null;
  pips: number | null;
  profit_money?: number;
  status: "Open" | "Closed";
  confidence: number;
}

export interface BacktestMetrics {
  initial_balance?: number;
  final_balance?: number;
  total_profit_money?: number;
  total_pips: number;
  total_trades: number;
  closed_trades: number;
  open_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  avg_win_money?: number;
  avg_loss_money?: number;
  profit_factor: number;
  period_days?: number;
  max_drawdown_percent?: number;
  max_drawdown_amount?: number;
  max_daily_drawdown_percent?: number;
}

export interface EquityPoint {
  timestamp: string;
  balance?: number;
  pips: number;
}

export interface BacktestResults {
  trades: Trade[];
  metrics: BacktestMetrics;
  equity_curve: EquityPoint[];
  monthly_performance?: {
    month: string;
    percent: number;
    profit: number;
  }[];
  daily_performance?: {
    [date: string]: {
      profit: number;
      percent: number;
      count: number;
    };
  };
  drawdown_curve?: {
    timestamp: string;
    drawdown: number;
  }[];
  output: string;
  timestamp: string;
}

export interface Config {
  indicators: {
    rsi_period: number;
    macd_fast: number;
    macd_slow: number;
    macd_signal: number;
    bb_period: number;
    bb_std_dev: number;
    atr_period: number;
    ema_fast: number;
    ema_slow: number;
  };
  risk: {
    stop_loss_percent: number;
    take_profit_percent: number;
    prob_threshold: number;
    use_atr_stops: boolean;
    use_trend_filter: boolean;
    use_volatility_filter: boolean;
    atr_filter_min: number;
    atr_filter_max: number;
  };
  model: {
    model_type: "xgboost" | "lightgbm" | "rf" | "ensemble";
    n_estimators: number;
    max_depth: number;
    min_samples_split: number;
  };
  data: {
    ticker: string;
    interval: string;
    training_period: string;
    mt5_csv_path: string;
  };
}

export interface DataFile {
  name: string;
  path: string;
  size: number;
  modified: string;
}

export interface Strategy {
  id: string;
  name: string;
  owner_id?: string;
  is_published?: boolean;
  created_at?: string;
  training: {
    params: TrainingParams;
    metadata: any;
    timestamp: string;
  };
  backtest: BacktestResults;
}

export interface User {
  id: string;
  email: string;
  token: string;
}

export interface AuthResponse {
  message: string;
  user?: User;
  error?: string;
}
