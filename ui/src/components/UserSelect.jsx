import { useState } from "react";
import globesImg from "../assets/img/globes.jpg";
import violaImg from "../assets/img/viola.webp";
import robotImg from "../assets/img/robot.jpg";
import tamborineImg from "../assets/img/tambourine.jpg";
import cubeImg from "../assets/img/cube.jpg";

const UserSelect = () => {
  const [options, setOptions] = useState([
    { id: 1, name: "Robot", img: robotImg, isChosen: false },
    { id: 2, name: "Tambourine", img: tamborineImg, isChosen: false },
    { id: 3, name: "Viola", img: violaImg, isChosen: false },
    { id: 4, name: "Rubik's Cube", img: cubeImg, isChosen: false },
  ]);

  const handleOptionClick = (id) => {
    setOptions((prevOptions) =>
      prevOptions.map((option) =>
        option.id === id ? { ...option, isChosen: true } : option
      )
    );

    const optionElement = document.querySelector(
      `.option--${id === 1 ? "first" : "second"}`
    );
    if (optionElement) {
      optionElement.classList.toggle(
        id === 1 ? "translate-left" : "translate-right"
      );
    }
  };

  const visibleOptions = options
    .filter((option) => !option.isChosen)
    .slice(0, 2);

  return (
    <div className="option__wrapper">
      {visibleOptions.length === 1 ? (
        <div className="option__border">
          <div className="option--single">
            <img
              className="option__img option__img--single"
              src={globesImg}
              alt={"Christmas Image"}
            />
            <h2 className="option__title--single">
              Your preferences were saved <br /> and sent to <span>Santa</span>
            </h2>
          </div>
        </div>
      ) : (
        <div className="multiple__options">
          <h2 className="option__title">Choose your gift preference</h2>
          <div className="option__container">
            {visibleOptions.map((option, index) => (
              <div
                key={option.id}
                className={`option ${
                  index === 0 ? "option--first" : "option--second"
                }`}
                onClick={() => handleOptionClick(option.id)}
              >
                <img
                  className="option__img"
                  src={option.img}
                  alt={option.name}
                />
                <h2 className="option__name">{option.name}</h2>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserSelect;
