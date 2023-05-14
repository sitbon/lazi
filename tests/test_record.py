import _lazi


@_lazi.param
def test_record_gen(use_lazi, _use_lazi=...):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_record_gen, _use_lazi=use_lazi)

    assert _use_lazi is not False or _use_lazi is ...

    with _lazi.ensure() as (lazi, mod):
        # TODO: More inspection of record stuff here.
        assert list(lazi.used()) or _use_lazi is ..., lazi.Finder.refs
