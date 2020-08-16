git pull
python -m pip install -U pip
pip install -U -r requirements.txt
python bot.py
cp quotes.db ../
sh ./scripts/update_db.sh
