# -*- coding: utf-8 -*-


from odoo.report import report_sxw


def formatLang(env, value, digits=None, grouping=True, monetary=False,
               dp=False, currency_obj=False):
    rml_parser = report_sxw.rml_parse(
        env.cr, env.uid, 'format_lang_wrapper', context=env.context)
    return rml_parser.formatLang(
        value, digits=digits, grouping=grouping, monetary=monetary, dp=dp,
        currency_obj=currency_obj)
