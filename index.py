import streamlit as st
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
from stellar_sdk.exceptions import NotFoundError

# Connect to Stellar Testnet
server = Server("https://horizon-testnet.stellar.org")

# Generate a temporary keypair for demo purposes
keypair = Keypair.random()
public_key = keypair.public_key
secret_key = keypair.secret

# Streamlit App UI
st.set_page_config(page_title="Stellar XLM Sender", layout="centered")
st.title("🚀 Stellar XLM Payment App (Testnet)")
st.markdown(f"**Your Public Key:** `{public_key}`")
st.markdown(f"[🔗 Fund your test account with Friendbot](https://friendbot.stellar.org/?addr={public_key})")
st.info("Use the Friendbot link above to add test XLM to your temporary account.")

st.markdown("---")

# User Inputs
destination_account = st.text_input("📥 Destination Account (Public Key)", placeholder="Enter a valid Stellar address")
amount = st.number_input("💰 Amount to Send (XLM)", min_value=0.1, step=0.1, format="%.7f")

# Submit Button
if st.button("📤 Send XLM"):
    if not destination_account or not amount:
        st.warning("Please fill in both destination and amount.")
        st.stop()

    # Check if sender account exists
    try:
        account_data = server.accounts().account_id(public_key).call()
        source_account = Account(account_id=public_key, sequence=str(account_data['sequence']))
    except NotFoundError:
        st.error("Account not found. Fund it using Friendbot and try again.")
        st.stop()

    try:
        # Build and sign the transaction
        transaction = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_payment_op(destination=destination_account, amount=str(amount), asset_code="XLM")
            .set_timeout(30)
            .build()
        )
        transaction.sign(keypair)

        # Submit the transaction
        response = server.submit_transaction(transaction)
        st.success("✅ Transaction successful!")
        st.json(response)
    except Exception as e:
        st.error(f"❌ Transaction failed: {e}")
