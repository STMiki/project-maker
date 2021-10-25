#include <iostream>

#include <SFML/Window.hpp>
#include <SFML/Graphics.hpp>

int main()
{
    sf::RenderWindow window({1280, 720}, "SFML");
    window.setFramerateLimit(60);
    window.setKeyRepeatEnabled(false);

    while (window.isOpen()) {
        sf::Event e;
        while (window.pollEvent(e)) {
            switch (e.type) {
                case sf::Event::Closed:
                    window.close();
                    break;

                default:
                    break;
            }
        }
        window.clear();
        window.display();
    }
}
