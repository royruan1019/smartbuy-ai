"""
模組名稱: scripts.update_agri_price_daily
功能說明: 抓取農業部農產品交易行情資料，並寫入 Supabase agri_price_daily。
"""

from __future__ import annotations

from pathlib import Path
import sys
import tomllib

from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.data.fetch_agri_prices import fetch_agri_prices  # noqa: E402


def load_database_url() -> str:
    """
    從 .streamlit/secrets.toml 讀取 DATABASE_URL。

    注意：
    .streamlit/secrets.toml 不可以 commit 到 GitHub。
    """
    secrets_path = PROJECT_ROOT / ".streamlit" / "secrets.toml"

    if not secrets_path.exists():
        raise FileNotFoundError(
            "找不到 .streamlit/secrets.toml，請先建立 DATABASE_URL。"
        )

    with secrets_path.open("rb") as file:
        secrets = tomllib.load(file)

    database_url = secrets.get("DATABASE_URL")

    if not database_url:
        raise ValueError("secrets.toml 中找不到 DATABASE_URL。")

    return database_url


def write_log(
    conn,
    status: str,
    rows_inserted: int = 0,
    rows_updated: int = 0,
    error_message: str | None = None,
) -> None:
    """寫入資料更新紀錄。"""
    conn.execute(
        text(
            """
            INSERT INTO data_update_logs (
                job_name,
                status,
                rows_inserted,
                rows_updated,
                error_message
            )
            VALUES (
                'update_agri_price_daily',
                :status,
                :rows_inserted,
                :rows_updated,
                :error_message
            );
            """
        ),
        {
            "status": status,
            "rows_inserted": rows_inserted,
            "rows_updated": rows_updated,
            "error_message": error_message,
        },
    )


def upsert_agri_prices() -> None:
    """
    抓取農產品交易行情，並以 upsert 寫入 agri_price_daily。

    判斷依據：
    trans_date + crop_code + market_code
    """
    database_url = load_database_url()
    engine = create_engine(database_url, pool_pre_ping=True)

    df = fetch_agri_prices()

    if df.empty:
        with engine.begin() as conn:
            write_log(
                conn,
                status="failed",
                error_message="API 有回應，但整理後沒有可寫入資料。",
            )

        print("沒有可寫入資料。")
        return

    insert_count = 0
    update_count = 0

    upsert_sql = text(
        """
        INSERT INTO agri_price_daily (
            trans_date,
            crop_code,
            crop_name,
            market_code,
            market_name,
            upper_price,
            middle_price,
            lower_price,
            avg_price,
            volume,
            source,
            updated_at
        )
        VALUES (
            :trans_date,
            :crop_code,
            :crop_name,
            :market_code,
            :market_name,
            :upper_price,
            :middle_price,
            :lower_price,
            :avg_price,
            :volume,
            'MOA_FarmTransData',
            NOW()
        )
        ON CONFLICT (trans_date, crop_code, market_code)
        DO UPDATE SET
            crop_name = EXCLUDED.crop_name,
            market_name = EXCLUDED.market_name,
            upper_price = EXCLUDED.upper_price,
            middle_price = EXCLUDED.middle_price,
            lower_price = EXCLUDED.lower_price,
            avg_price = EXCLUDED.avg_price,
            volume = EXCLUDED.volume,
            source = EXCLUDED.source,
            updated_at = NOW();
        """
    )

    exists_sql = text(
        """
        SELECT 1
        FROM agri_price_daily
        WHERE trans_date = :trans_date
          AND crop_code = :crop_code
          AND market_code = :market_code
        LIMIT 1;
        """
    )

    try:
        with engine.begin() as conn:
            for row in df.to_dict(orient="records"):
                exists = conn.execute(
                    exists_sql,
                    {
                        "trans_date": row["trans_date"],
                        "crop_code": row["crop_code"],
                        "market_code": row["market_code"],
                    },
                ).first()

                conn.execute(upsert_sql, row)

                if exists:
                    update_count += 1
                else:
                    insert_count += 1

            write_log(
                conn,
                status="success",
                rows_inserted=insert_count,
                rows_updated=update_count,
            )

        print("農產品交易行情更新完成。")
        print(f"新增筆數：{insert_count}")
        print(f"更新筆數：{update_count}")

    except Exception as exc:
        with engine.begin() as conn:
            write_log(
                conn,
                status="failed",
                error_message=str(exc),
            )

        raise


if __name__ == "__main__":
    upsert_agri_prices()