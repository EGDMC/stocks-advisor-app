-- Create market_data table
create table market_data (
  id bigint primary key generated always as identity,
  date date not null,
  open numeric not null,
  high numeric not null,
  low numeric not null,
  close numeric not null,
  volume bigint not null,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create index on date
create index idx_market_data_date on market_data(date);

-- Create analysis_results table
create table analysis_results (
  id bigint primary key generated always as identity,
  type text not null,
  trend text not null,
  prediction text not null,
  confidence numeric not null,
  recommendation text not null,
  summary text not null,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create model_predictions table
create table model_predictions (
  id bigint primary key generated always as identity,
  date date not null,
  predicted_price numeric not null,
  confidence numeric not null,
  direction text not null,
  features jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create index on prediction date
create index idx_model_predictions_date on model_predictions(date);