def switch_to_app_manager(stack):
    print("Opening App Manager...")
    stack.setCurrentIndex(1)

def switch_to_main(stack):
    print("Returning to Main Page")
    stack.setCurrentIndex(0)
