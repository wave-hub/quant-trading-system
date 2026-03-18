"""Strategy code generator from React Flow canvas data."""

from typing import Dict, Any, List

class CodeGenerator:
    """策略生成器：从可视化画板节点生成 Python 代码格式"""

    def __init__(self, canvas_data: Dict[str, Any]):
        self.nodes = canvas_data.get('nodes', [])
        self.edges = canvas_data.get('edges', [])
        self.node_map = {n['id']: n for n in self.nodes}

    def generate(self) -> str:
        """解析画布生成 Python 代码"""
        if not self.nodes:
            return ""

        # Find the starting nodes (Data Source usually)
        data_nodes = [n for n in self.nodes if n['type'] == 'data']

        code_lines = []
        code_lines.append("def init(context):")
        code_lines.append("    # Visual Builder Generated Initialization")
        
        # 提取标的名称（目前假设只有一个标的，作为演示缩影）
        symbols = []
        for node in data_nodes:
            label = node.get('data', {}).get('label', '')
            if '沪深300' in label:
                symbols.append("'399300.SZ'")
            else:
                symbols.append("'000001.SZ'")
                
        symbol_list_str = "[" + ", ".join(symbols) + "]" if symbols else "[]"
        code_lines.append(f"    context.universe = {symbol_list_str}")
        code_lines.append("")

        code_lines.append("def handle_bar(context, bar_dict):")
        code_lines.append("    # Visual Builder Generated Logic")
        code_lines.append("    for stock in context.universe:")
        
        # 识别技术指标
        indicator_nodes = [n for n in self.nodes if n['type'] == 'indicator']    
        for node in indicator_nodes:
            label = node.get('data', {}).get('label', '')
            if 'MA' in label:
                code_lines.append(f"        history = context.history(stock, 'close', 20, '1d')")
                code_lines.append(f"        ma20 = history.mean()")
        
        # 识别信号处理与买卖
        signal_nodes = [n for n in self.nodes if n['type'] == 'signal']
        action_nodes = [n for n in self.nodes if n['type'] == 'action']
        
        has_buy_action = any('买入' in n.get('data', {}).get('label', '') for n in action_nodes)
        has_sell_action = any('卖出' in n.get('data', {}).get('label', '') for n in action_nodes)
        
        if signal_nodes:
            code_lines.append("        current_price = bar_dict[stock].close")
            code_lines.append("        if current_price > ma20:")
            if has_buy_action:
                code_lines.append("            order_target_percent(stock, 1.0)")
            else:
                code_lines.append("            pass")
            
            code_lines.append("        elif current_price < ma20:")
            if has_sell_action:
                code_lines.append("            order_target_percent(stock, 0.0)")
            elif has_buy_action:
                code_lines.append("            order_target_percent(stock, 0.0) # default stop loss")
            else:
                code_lines.append("            pass")

        # Fallback if canvas has only actions without signals
        if not signal_nodes and action_nodes:
             if has_buy_action:
                 code_lines.append("        order_target_percent(stock, 1.0) # Unconditional buy")

        if not indicator_nodes and not signal_nodes and not action_nodes:
            code_lines.append("        pass")

        return "\n".join(code_lines)
