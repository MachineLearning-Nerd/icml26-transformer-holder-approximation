from src.claim1_direct_cpu_audit import audit, upper_blocks
def test_source_and_rate_probe():
 r=audit(); assert r['all_source_conditions_found']; assert r['cpu_rate_probe']['ratio']==r['cpu_rate_probe']['expected_ratio']
def test_dimension_control(): assert upper_blocks(.5,4,1)==16
