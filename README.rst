========================
DragonQuest 9 Grotto Bot
========================
Created using Python 3.8.2 to fill the sole purpose of acting as a website "wrapper" around the `grotto search tool <https://www.yabd.org/apps/dq9/grottosearch.php>`_ by GameFAQs user `Yab. <https://gamefaqs.gamespot.com/community/yab>`_ (`Site <http://www.yabd.org>`_) The functionality of which is tucked into a convenient, server-unique Discord bot for `Dragon Quest IX: Fan Server. <https://discord.gg/NGZ6RKB>`_


Differences Between Grotto Bot And Public Bots
----------------------------------------------
Grotto Bot is mostly Flake8-compliant, meaning that the source code adheres to a majority of `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ but this will not matter for developers disassociated with Grotot Bot. Alongside that, this is also an exclusive Discord bot dedicated to the aforementioned server and can/will be discontinued along with the server owner's instruction or if the server happens to follow an untimely demise.


Thoughts On Personal Usage
--------------------------
While Grotto Bot is made to be readable, this is a version that is dedicated to a specific use case and would therefore be exhaustive to configure for alternate needs. Hosting Grotto Bot is not entirely advisable and I therefore encourage you to look into expanding on the examples provided in the Discord.py repository, specifically `here. <https://github.com/Rapptz/discord.py/blob/master/examples/basic_bot.py>`_

That being said, for those with determined interests, below are the requirements and the necessary knowledge to aid you in running your own personal Grotto Bot.


Prerequisites
-------------
- Python 3.8.2+
- `Git <https://git-scm.com/downloads>`_
- Pip (should come pre-installed with default Python)

Note
~~~~
These libraries are also included within this repository's ``requirements.txt`` for an easier installation

- `Discord.py <https://pypi.org/project/discord.py/>`_ (Discord API wrapper, voice is not used) 1.3.3
- `Parsel <https://pypi.org/project/parsel/>`_ (HTML/XML parser) 1.6.0


Setup
-----
.. code:: sh

    git clone https://github.com/cyrus01337/dq9-grotto-bot.git
    cd dq9-grotto-bot

    # For those using a virtualenv
    # For Unix, use pip3
    pip install -r requirements.txt

Along with the repository you require an additional file named ``_token.py``, containing a synchronous function ``get()`` that returns your Discord bot token. The method used is subjective, however replacing this functionality to instead use coroutines requires manually editing ``bot.py``.

Upon completion Grotto Bot will work like any other Python file:

.. code:: sh

    # .../dq9-grotto-bot/
    # Windows
    py -3 bot.py

    # Linux/macOS
    python3.8 bot.py
