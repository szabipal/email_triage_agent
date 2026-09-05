def test_package_import() -> None:
    import email_agent

    assert email_agent.__name__ == "email_agent"
