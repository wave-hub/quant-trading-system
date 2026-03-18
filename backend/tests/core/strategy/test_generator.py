from backend.core.strategy.visual_builder.generator import CodeGenerator

def test_code_generator_buy_signal():
    canvas_data = {
        "nodes": [
            {"id": "node-1", "type": "data", "data": {"label": "沪深300指数"}},
            {"id": "node-2", "type": "indicator", "data": {"label": "计算 MA20"}},
            {"id": "node-3", "type": "signal", "data": {"label": "价格 > MA20"}},
            {"id": "node-4", "type": "action", "data": {"label": "全仓买入"}}
        ],
        "edges": []
    }
    generator = CodeGenerator(canvas_data)
    code = generator.generate()
    
    assert "def init(context):" in code
    assert "context.universe = ['399300.SZ']" in code
    assert "ma20 = history.mean()" in code
    assert "order_target_percent(stock, 1.0)" in code

def test_code_generator_empty():
    generator = CodeGenerator({"nodes": []})
    assert generator.generate() == ""
